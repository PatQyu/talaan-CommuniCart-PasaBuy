const groceryForm = document.getElementById('grocery-form');
const receiptItems = document.getElementById('receipt-items');
const receiptTotal = document.getElementById('receipt-total');
const budgetValue = document.getElementById('budget-value');
const remainingValue = document.getElementById('remaining-value');
const receiptMeta = document.getElementById('receipt-meta');
const formStatus = document.getElementById('form-status');
const mapStatus = document.getElementById('map-status');
const findStoresBtn = document.getElementById('find-stores-btn');
const storeList = document.getElementById('store-list');

let latestReceipt = [];
let mapInstance = null;
let mapMarkers = [];

function currencyPhp(value) {
    return `PHP ${Number(value || 0).toFixed(2)}`;
}

function parseRawItems(text) {
    return text
        .split('\n')
        .map((item) => item.trim())
        .filter(Boolean);
}

function renderReceiptRow(receiptItem, index) {
    const selected = receiptItem.selected;
    const alternatives = receiptItem.alternatives || [];

    const tr = document.createElement('tr');
    tr.dataset.index = String(index);

    tr.innerHTML = `
        <td class="product-name"><strong>${selected.product_name}</strong></td>
        <td class="brand-name">${selected.brand_name || 'N/A'}</td>
        <td class="qty-cell">${selected.calculated_qty}</td>
        <td class="unit-price" data-price="${selected.price}">${currencyPhp(selected.price)}</td>
        <td class="subtotal-price" data-subtotal="${selected.subtotal}">${currencyPhp(selected.subtotal)}</td>
        <td>
            <select class="alt-select" ${alternatives.length === 0 ? 'disabled' : ''} aria-label="Alternative options selection">
                <option value="">${alternatives.length ? 'Switch product option...' : 'No alternatives available'}</option>
                ${alternatives.map((alt, altIndex) => `
                    <option value="${altIndex}">${alt.product_name} (${alt.brand_name || 'N/A'}) - ${currencyPhp(alt.price)}</option>
                `).join('')}
            </select>
        </td>
    `;

    const select = tr.querySelector('.alt-select');
    if (alternatives.length > 0) {
        select.addEventListener('change', () => switchAlternative(index, Number(select.value)));
    }

    return tr;
}

function renderReceipt(receipt) {
    latestReceipt = receipt;
    receiptItems.innerHTML = '';

    if (receipt.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.innerHTML = '<td colspan="6">No items generated yet. Submit your requirements to begin.</td>';
        receiptItems.appendChild(emptyRow);
        refreshTotals();
        return;
    }

    receipt.forEach((item, index) => {
        receiptItems.appendChild(renderReceiptRow(item, index));
    });

    refreshTotals();
}

function refreshTotals() {
    const total = latestReceipt.reduce((sum, item) => sum + Number(item.selected.subtotal || 0), 0);
    receiptTotal.textContent = currencyPhp(total);
}

function switchAlternative(receiptIndex, altIndex) {
    const receiptItem = latestReceipt[receiptIndex];
    if (!receiptItem || Number.isNaN(altIndex) || altIndex < 0) {
        return;
    }

    const currentSelected = receiptItem.selected;
    const alternatives = receiptItem.alternatives || [];
    const newSelected = alternatives[altIndex];

    if (!newSelected) {
        return;
    }

    const qty = Number(currentSelected.calculated_qty || 1);
    const switched = {
        ...newSelected,
        calculated_qty: qty,
        subtotal: Number(newSelected.price) * qty
    };

    const preservedAlternatives = alternatives.filter((_, idx) => idx !== altIndex);
    preservedAlternatives.unshift({
        product_id: currentSelected.product_id,
        product_name: currentSelected.product_name,
        brand_name: currentSelected.brand_name,
        price: Number(currentSelected.price)
    });

    latestReceipt[receiptIndex] = {
        selected: switched,
        alternatives: preservedAlternatives
    };

    renderReceipt(latestReceipt);
}

async function submitGroceryForm(event) {
    event.preventDefault();
    formStatus.textContent = 'Generating grocery list via Gemini API...';

    const formData = new FormData(groceryForm);
    const rawItemsText = String(formData.get('raw_items') || '');

    const payload = {
        budget: Number(formData.get('budget')),
        elderly_count: Number(formData.get('elderly_count')),
        adult_count: Number(formData.get('adult_count')),
        teen_count: Number(formData.get('teen_count')),
        children_count: Number(formData.get('children_count')),
        ration_days: Number(formData.get('ration_days')),
        raw_items: parseRawItems(rawItemsText)
    };

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok || data.status !== 'success') {
            throw new Error(data.message || 'Failed to calculate grocery list.');
        }

        renderReceipt(data.receipt || []);
        budgetValue.textContent = currencyPhp(data.original_budget);
        remainingValue.textContent = currencyPhp(data.remaining_balance);
        receiptMeta.textContent = `Generated ${data.receipt.length} items.`;
        formStatus.textContent = 'Receipt generated successfully.';
    } catch (error) {
        formStatus.textContent = error.message;
    }
}

function clearMarkers() {
    mapMarkers.forEach((marker) => marker.setMap(null));
    mapMarkers = [];
}

function renderStoreList(stores) {
    storeList.innerHTML = '';

    if (!stores.length) {
        const li = document.createElement('li');
        li.textContent = 'No nearby stores found matching criteria.';
        storeList.appendChild(li);
        return;
    }

    stores.forEach((store) => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${store.name}</strong><span>${store.address || 'No address available'}</span>`;
        storeList.appendChild(li);
    });
}

async function fetchNearbyStores() {
    mapStatus.textContent = 'Acquiring geolocation telemetry...';

    if (!navigator.geolocation) {
        mapStatus.textContent = 'Geolocation is not supported in this browser.';
        return;
    }

    navigator.geolocation.getCurrentPosition(async (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        mapStatus.textContent = 'Querying Google Maps for neighborhood stores...';

        try {
            const response = await fetch('/nearby-stores', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ lat, lng })
            });

            const data = await response.json();
            if (!response.ok || data.status !== 'success') {
                throw new Error(data.message || 'Failed to get nearby stores.');
            }

            const stores = data.stores || [];
            renderStoreList(stores);
            plotStoresOnMap(lat, lng, stores);
            mapStatus.textContent = `Found ${stores.length} distribution outlets.`;
        } catch (error) {
            mapStatus.textContent = error.message;
        }
    }, (error) => {
        mapStatus.textContent = `Location clearance error: ${error.message}`;
    });
}

function plotStoresOnMap(userLat, userLng, stores) {
    if (!mapInstance || typeof google === 'undefined' || !google.maps) {
        return;
    }

    clearMarkers();

    const userLocation = { lat: userLat, lng: userLng };
    mapInstance.setCenter(userLocation);
    mapInstance.setZoom(13);

    const userMarker = new google.maps.Marker({
        map: mapInstance,
        position: userLocation,
        title: 'Your Location'
    });
    mapMarkers.push(userMarker);

    stores.forEach((store) => {
        const marker = new google.maps.Marker({
            map: mapInstance,
            position: { lat: store.lat, lng: store.lng },
            title: store.name
        });
        mapMarkers.push(marker);
    });
}

window.initMap = function initMap() {
    const mapEl = document.getElementById('map');
    if (!mapEl) {
        return;
    }

    mapInstance = new google.maps.Map(mapEl, {
        center: { lat: 14.5995, lng: 120.9842 },
        zoom: 11,
        streetViewControl: false,
        mapTypeControl: false
    });
};

if (groceryForm) {
    groceryForm.addEventListener('submit', submitGroceryForm);
}

if (findStoresBtn) {
    findStoresBtn.addEventListener('click', fetchNearbyStores);
}

if (!window.APP_CONFIG || !window.APP_CONFIG.mapsApiKey) {
    mapStatus.textContent = 'Google Maps API key is missing. Map preview is disabled, but nearby store list still works.';
}

renderReceipt([]);
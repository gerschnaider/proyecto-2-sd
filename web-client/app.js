const PORTS = {
    areaManager: 8080,
    subscriptions: 8004,
    publish: 50050,
    getLoad: 8003,
    findDescriptor: 8030,
    last24h: 8005,
    findPeriod: 8002,
    deleteNews: 8001
};

function getBaseUrl(port) {
    const ip = document.getElementById('cluster-ip').value || 'localhost';
    return `http://${ip}:${port}`;
}

function logOutput(operation, data, isError = false) {
    const outputLog = document.getElementById('output-log');
    const timestamp = new Date().toLocaleTimeString();
    const prefix = isError ? '[ERROR]' : '[SUCCESS]';
    
    let formattedData;
    try {
        formattedData = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
    } catch {
        formattedData = data;
    }

    const logEntry = `\n> ${timestamp} ${prefix} ${operation}\n${formattedData}\n`;
    if (outputLog.textContent === "Esperando operaciones...") {
        outputLog.textContent = "";
    }
    outputLog.textContent += logEntry;
    outputLog.scrollTop = outputLog.scrollHeight;
}

function clearConsole() {
    document.getElementById('output-log').textContent = "Esperando operaciones...";
}

async function apiCall(port, endpoint, method, body = null) {
    const url = `${getBaseUrl(port)}${endpoint}`;
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        let data;
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            data = await response.json();
        } else {
            data = await response.text();
        }
        
        if (!response.ok) {
            logOutput(`${method} ${endpoint}`, data, true);
            return null;
        }
        logOutput(`${method} ${endpoint}`, data);
        return data;
    } catch (error) {
        logOutput(`${method} ${endpoint}`, `Fallo de conexión. ¿Problema de CORS o servidor caído? Detalles: ${error.message}`, true);
        return null;
    }
}

// Actions
async function createArea() {
    const name = document.getElementById('area-name').value;
    const userId = parseInt(document.getElementById('area-user-id').value);
    await apiCall(PORTS.areaManager, '/areas', 'POST', { name, user_id: userId });
}

async function deleteArea() {
    const name = encodeURIComponent(document.getElementById('area-name').value);
    const userId = parseInt(document.getElementById('area-user-id').value);
    await apiCall(PORTS.areaManager, `/areas/${name}`, 'DELETE', { user_id: userId });
}

async function subscribe() {
    const categoryId = parseInt(document.getElementById('sub-category-id').value);
    const userId = parseInt(document.getElementById('sub-user-id').value);
    await apiCall(PORTS.subscriptions, '/suscribir', 'POST', { user_id: userId, category_id: categoryId });
}

async function unsubscribe() {
    const categoryId = parseInt(document.getElementById('sub-category-id').value);
    const userId = parseInt(document.getElementById('sub-user-id').value);
    await apiCall(PORTS.subscriptions, '/desuscribir', 'DELETE', { user_id: userId, category_id: categoryId });
}

async function publishNews() {
    const title = document.getElementById('pub-title').value;
    const categoryId = parseInt(document.getElementById('pub-category-id').value);
    const userId = parseInt(document.getElementById('pub-user-id').value);
    const text = document.getElementById('pub-content').value;
    
    await apiCall(PORTS.publish, '/api/noticias', 'POST', {
        titulo: title,
        id_autor: userId,
        id_categoria: categoryId,
        texto: text
    });
}

async function getNewsLoad() {
    await apiCall(PORTS.getLoad, '/api/news-load', 'GET');
}

async function findNewsByDescriptor() {
    const descriptor = encodeURIComponent(document.getElementById('q-descriptor').value);
    await apiCall(PORTS.findDescriptor, `/api/news-descriptor?descriptor=${descriptor}`, 'GET');
}

async function getLast24h() {
    const userId = document.getElementById('q-user-id').value;
    await apiCall(PORTS.last24h, `/api/news-last-24h?user_id=${userId}`, 'GET');
}

async function findNewsPeriod() {
    const start = document.getElementById('q-start').value;
    const end = document.getElementById('q-end').value;
    await apiCall(PORTS.findPeriod, `/api/news-period?fecha_inicio=${start}&fecha_fin=${end}`, 'GET');
}

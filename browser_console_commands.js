// ========================================
// КОМАНДЫ ДЛЯ ВЫПОЛНЕНИЯ В КОНСОЛИ БРАУЗЕРА
// ========================================

// 1. ПОЛУЧИТЬ ПОЛНУЮ HTML СТРУКТУРУ СТРАНИЦЫ
// ========================================
console.log("=== ПОЛНАЯ HTML СТРУКТУРА СТРАНИЦЫ ===");
console.log(document.documentElement.outerHTML);

// 2. АНАЛИЗ ЭЛЕМЕНТОВ REPORTVIEWER
// ========================================
console.log("=== ЭЛЕМЕНТЫ REPORTVIEWER ===");
const reportElements = document.querySelectorAll('[id*="ReportViewer"], [class*="ReportViewer"]');
console.log(`Найдено элементов ReportViewer: ${reportElements.length}`);
reportElements.forEach((el, i) => {
    console.log(`${i+1}. ID: ${el.id}, Class: ${el.className}, Tag: ${el.tagName}`);
});

// 3. АНАЛИЗ ТАБЛИЦ ДАННЫХ
// ========================================
console.log("=== ТАБЛИЦЫ ДАННЫХ ===");
const dataTables = document.querySelectorAll('table[class*="data"], table[id*="data"], table[class*="table"]');
console.log(`Найдено таблиц данных: ${dataTables.length}`);
dataTables.forEach((table, i) => {
    console.log(`${i+1}. ID: ${table.id}, Class: ${table.className}`);
    console.log(`   Строк: ${table.rows.length}, Колонок: ${table.rows[0]?.cells.length || 0}`);
});

// 4. АНАЛИЗ ЭЛЕМЕНТОВ ПАГИНАЦИИ
// ========================================
console.log("=== ЭЛЕМЕНТЫ ПАГИНАЦИИ ===");
const paginationElements = document.querySelectorAll('[class*="pagination"], [id*="pagination"], *:contains("Страница")');
console.log(`Найдено элементов пагинации: ${paginationElements.length}`);
paginationElements.forEach((el, i) => {
    console.log(`${i+1}. ID: ${el.id}, Class: ${el.className}, Text: ${el.textContent.trim()}`);
});

// 5. АНАЛИЗ ЭЛЕМЕНТОВ ЭКСПОРТА
// ========================================
console.log("=== ЭЛЕМЕНТЫ ЭКСПОРТА ===");
const exportElements = document.querySelectorAll('[class*="export"], [id*="export"], *:contains("Экспорт"), *:contains("Excel")');
console.log(`Найдено элементов экспорта: ${exportElements.length}`);
exportElements.forEach((el, i) => {
    console.log(`${i+1}. ID: ${el.id}, Class: ${el.className}, Text: ${el.textContent.trim()}`);
});

// 6. АНАЛИЗ СКРЫТЫХ ПОЛЕЙ С ДАННЫМИ
// ========================================
console.log("=== СКРЫТЫЕ ПОЛЯ С ДАННЫМИ ===");
const hiddenDataFields = document.querySelectorAll('input[type="hidden"][value*="data"]');
console.log(`Найдено скрытых полей с данными: ${hiddenDataFields.length}`);
hiddenDataFields.forEach((field, i) => {
    console.log(`${i+1}. ID: ${field.id}, Name: ${field.name}, Value: ${field.value}`);
});

// 7. ПОИСК ВСЕХ КНОПОК И ИХ ТЕКСТА
// ========================================
console.log("=== ВСЕ КНОПКИ ===");
const allButtons = document.querySelectorAll('button, input[type="button"], input[type="submit"], a[role="button"]');
console.log(`Найдено кнопок: ${allButtons.length}`);
allButtons.forEach((btn, i) => {
    console.log(`${i+1}. ID: ${btn.id}, Class: ${btn.className}, Text: "${btn.textContent.trim()}", Tag: ${btn.tagName}`);
});

// 8. ПОИСК ВСЕХ ПОЛЕЙ ВВОДА
// ========================================
console.log("=== ВСЕ ПОЛИ ВВОДА ===");
const allInputs = document.querySelectorAll('input, select, textarea');
console.log(`Найдено полей ввода: ${allInputs.length}`);
allInputs.forEach((input, i) => {
    console.log(`${i+1}. ID: ${input.id}, Name: ${input.name}, Type: ${input.type}, Class: ${input.className}`);
});

// 9. КОПИРОВАНИЕ ВСЕГО В БУФЕР ОБМЕНА
// ========================================
console.log("=== КОПИРОВАНИЕ В БУФЕР ОБМЕНА ===");

// Функция для копирования в буфер обмена
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            console.log("✅ Текст скопирован в буфер обмена");
        }).catch(err => {
            console.error("❌ Ошибка копирования:", err);
        });
    } else {
        // Fallback для старых браузеров
        const textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
        console.log("✅ Текст скопирован в буфер обмена (fallback)");
    }
}

// Собираем всю информацию
const pageInfo = {
    url: window.location.href,
    title: document.title,
    timestamp: new Date().toISOString(),
    reportElements: Array.from(reportElements).map(el => ({
        id: el.id,
        className: el.className,
        tagName: el.tagName
    })),
    dataTables: Array.from(dataTables).map(table => ({
        id: table.id,
        className: table.className,
        rows: table.rows.length,
        columns: table.rows[0]?.cells.length || 0
    })),
    buttons: Array.from(allButtons).map(btn => ({
        id: btn.id,
        className: btn.className,
        text: btn.textContent.trim(),
        tagName: btn.tagName
    })),
    inputs: Array.from(allInputs).map(input => ({
        id: input.id,
        name: input.name,
        type: input.type,
        className: input.className
    })),
    html: document.documentElement.outerHTML
};

// Копируем в буфер обмена
copyToClipboard(JSON.stringify(pageInfo, null, 2));

console.log("🎯 Вся информация скопирована в буфер обмена!");
console.log("📋 Теперь можете вставить её в чат для анализа");

// 10. БЫСТРАЯ ПРОВЕРКА СЕТЕВЫХ ЗАПРОСОВ
// ========================================
console.log("=== СЕТЕВЫЕ ЗАПРОСЫ ===");
console.log("💡 Откройте вкладку Network в DevTools и обновите страницу");
console.log("🔍 Ищите запросы с типами: XHR, Fetch, Document");
console.log("📊 Особенно важны запросы к API для получения данных отчета");

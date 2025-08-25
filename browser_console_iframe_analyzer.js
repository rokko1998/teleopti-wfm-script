// Анализатор содержимого iframe'а с формой отчета Microsoft SQL Server Reporting Services
// Скопируйте весь этот код в консоль браузера (F12 -> Console) и нажмите Enter

console.log('🔍 Анализ содержимого iframe\'а с формой отчета...');

// Функция для получения информации об элементе
function getElementInfo(element) {
    if (!element) return 'Элемент не найден';

    return {
        tagName: element.tagName,
        id: element.id || 'Нет ID',
        name: element.name || 'Нет name',
        type: element.type || 'Нет type',
        className: element.className || 'Нет class',
        value: element.value || 'Нет value',
        placeholder: element.placeholder || 'Нет placeholder',
        textContent: element.textContent ? element.textContent.trim().substring(0, 100) : 'Нет текста',
        isVisible: element.offsetWidth > 0 && element.offsetHeight > 0,
        isEnabled: !element.disabled,
        isReadOnly: element.readOnly || false,
        title: element.title || 'Нет title',
        alt: element.alt || 'Нет alt'
    };
}

// Функция для анализа содержимого iframe'а
function analyzeIframeContent() {
    console.log('\n🖼️ АНАЛИЗ СОДЕРЖИМОГО IFRAME...');

    const iframes = document.querySelectorAll('iframe');
    if (iframes.length === 0) {
        console.log('❌ Iframe не найден');
        return;
    }

    const iframe = iframes[0]; // Берем первый iframe
    console.log(`✅ Найден iframe: ${iframe.src}`);

    try {
        if (!iframe.contentDocument) {
            console.log('❌ Нет доступа к содержимому iframe');
            return;
        }

        const iframeDoc = iframe.contentDocument;
        console.log('✅ Доступ к содержимому iframe получен');

        // 1. Анализируем все элементы формы в iframe
        console.log('\n📋 АНАЛИЗ ЭЛЕМЕНТОВ ФОРМЫ В IFRAME:');
        const allInputs = iframeDoc.querySelectorAll('input, select, textarea, button');
        console.log(`Всего элементов формы: ${allInputs.length}`);

        // Группируем элементы по типам
        const inputTypes = {};
        const elementsByType = {};

        allInputs.forEach((input, index) => {
            const type = input.type || input.tagName.toLowerCase();
            inputTypes[type] = (inputTypes[type] || 0) + 1;

            if (!elementsByType[type]) {
                elementsByType[type] = [];
            }
            elementsByType[type].push(input);
        });

        console.log('\n📊 РАСПРЕДЕЛЕНИЕ ПО ТИПАМ:');
        Object.entries(inputTypes).forEach(([type, count]) => {
            console.log(`   ${type}: ${count}`);
        });

        // 2. Ищем элементы по ключевым словам
        console.log('\n🔍 ПОИСК ЭЛЕМЕНТОВ ПО КЛЮЧЕВЫМ СЛОВАМ:');

        const keywords = [
            'период', 'period', 'тип', 'type',
            'дата', 'date', 'начало', 'start', 'с', 'from',
            'окончание', 'end', 'по', 'to', 'finish',
            'причина', 'reason', 'обращение', 'issue', 'cause',
            'отчет', 'report', 'сформировать', 'generate', 'просмотр', 'view'
        ];

        keywords.forEach(keyword => {
            const elements = iframeDoc.querySelectorAll('*');
            const foundElements = [];

            elements.forEach(element => {
                if (element.textContent && element.textContent.toLowerCase().includes(keyword.toLowerCase())) {
                    // Ищем ближайшие элементы формы
                    const nearbyFormElements = element.querySelectorAll('input, select, textarea, button');
                    if (nearbyFormElements.length > 0) {
                        foundElements.push({
                            text: element.textContent.trim().substring(0, 50),
                            nearbyElements: nearbyFormElements
                        });
                    }
                }
            });

            if (foundElements.length > 0) {
                console.log(`\nКлючевое слово "${keyword}": найдено ${foundElements.length} совпадений`);
                foundElements.forEach((item, index) => {
                    if (index < 3) {
                        console.log(`  ${index + 1}. Текст: "${item.text}"`);
                        console.log(`     Ближайшие элементы формы: ${item.nearbyElements.length}`);
                    }
                });
            }
        });

        // 3. Анализируем элементы по типам
        console.log('\n🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ЭЛЕМЕНТОВ ПО ТИПАМ:');

        Object.entries(elementsByType).forEach(([type, elements]) => {
            if (elements.length <= 10) {
                console.log(`\n${type.toUpperCase()} (${elements.length}):`);
                elements.forEach((element, index) => {
                    const info = getElementInfo(element);
                    console.log(`  ${index + 1}. ${element.tagName} - ID: ${info.id}, Name: ${info.name}, Class: ${info.className}`);
                    if (info.textContent) {
                        console.log(`     Текст: "${info.textContent}"`);
                    }
                });
            } else {
                console.log(`\n${type.toUpperCase()} (${elements.length}): показываем первые 10`);
                elements.slice(0, 10).forEach((element, index) => {
                    const info = getElementInfo(element);
                    console.log(`  ${index + 1}. ${element.tagName} - ID: ${info.id}, Name: ${info.name}, Class: ${info.className}`);
                });
                console.log(`  ... и еще ${elements.length - 10} элементов`);
            }
        });

        // 4. Ищем элементы с конкретными атрибутами
        console.log('\n🎯 ПОИСК ПО АТРИБУТАМ:');

        const attributeSelectors = [
            '[id*="period"]', '[id*="Period"]', '[id*="date"]', '[id*="Date"]',
            '[id*="start"]', '[id*="Start"]', '[id*="end"]', '[id*="End"]',
            '[id*="reason"]', '[id*="Reason"]', '[id*="cause"]', '[id*="Cause"]',
            '[name*="period"]', '[name*="Period"]', '[name*="date"]', '[name*="Date"]',
            '[name*="start"]', '[name*="Start"]', '[name*="end"]', '[name*="End"]',
            '[name*="reason"]', '[name*="Reason"]', '[name*="cause"]', '[name*="Cause"]',
            '[class*="period"]', '[class*="Period"]', '[class*="date"]', '[class*="Date"]',
            '[class*="start"]', '[class*="Start"]', '[class*="end"]', '[class*="End"]',
            '[class*="reason"]', '[class*="Reason"]', '[class*="cause"]', '[class*="Cause"]'
        ];

        attributeSelectors.forEach(selector => {
            try {
                const elements = iframeDoc.querySelectorAll(selector);
                if (elements.length > 0) {
                    console.log(`\nСелектор "${selector}": найдено ${elements.length} элементов`);
                    elements.forEach((el, index) => {
                        if (index < 3) {
                            const info = getElementInfo(el);
                            console.log(`  ${index + 1}. ${el.tagName} - ID: ${info.id}, Name: ${info.name}, Type: ${info.type}`);
                        }
                    });
                }
            } catch (error) {
                // Игнорируем ошибки селекторов
            }
        });

        // 5. Ищем элементы по тексту в label и span
        console.log('\n🏷️ ПОИСК МЕТОК И ТЕКСТА:');

        const labels = iframeDoc.querySelectorAll('label, span, div, td, th');
        const relevantLabels = [];

        labels.forEach(label => {
            const text = label.textContent ? label.textContent.trim() : '';
            if (text && text.length > 0 && text.length < 100) {
                const keywords = ['период', 'дата', 'причина', 'отчет', 'period', 'date', 'reason', 'report'];
                const hasKeyword = keywords.some(keyword => text.toLowerCase().includes(keyword.toLowerCase()));

                if (hasKeyword) {
                    relevantLabels.push({
                        element: label,
                        text: text,
                        tagName: label.tagName
                    });
                }
            }
        });

        if (relevantLabels.length > 0) {
            console.log(`Найдено ${relevantLabels.length} релевантных меток:`);
            relevantLabels.forEach((label, index) => {
                if (index < 10) {
                    console.log(`  ${index + 1}. ${label.tagName}: "${label.text}"`);

                    // Ищем ближайшие элементы формы
                    const nearbyFormElements = label.element.querySelectorAll('input, select, textarea, button');
                    if (nearbyFormElements.length > 0) {
                        console.log(`     Ближайшие элементы формы: ${nearbyFormElements.length}`);
                        nearbyFormElements.forEach((formEl, i) => {
                            if (i < 3) {
                                const info = getElementInfo(formEl);
                                console.log(`       ${i + 1}. ${formEl.tagName} - ID: ${info.id}, Name: ${info.name}, Type: ${info.type}`);
                            }
                        });
                    }
                }
            });
        }

        // 6. Анализируем структуру таблиц
        console.log('\n📊 АНАЛИЗ ТАБЛИЦ:');
        const tables = iframeDoc.querySelectorAll('table');
        console.log(`Найдено таблиц: ${tables.length}`);

        tables.forEach((table, index) => {
            if (index < 5) {
                const rows = table.querySelectorAll('tr');
                const cells = table.querySelectorAll('td, th');
                console.log(`\nТаблица ${index + 1}: ${rows.length} строк, ${cells.length} ячеек`);

                // Ищем ячейки с ключевыми словами
                const relevantCells = [];
                cells.forEach(cell => {
                    const text = cell.textContent ? cell.textContent.trim() : '';
                    if (text && text.length > 0 && text.length < 100) {
                        const keywords = ['период', 'дата', 'причина', 'отчет', 'period', 'date', 'reason', 'report'];
                        const hasKeyword = keywords.some(keyword => text.toLowerCase().includes(keyword.toLowerCase()));

                        if (hasKeyword) {
                            relevantCells.push({
                                text: text,
                                hasFormElements: cell.querySelectorAll('input, select, textarea, button').length > 0
                            });
                        }
                    }
                });

                if (relevantCells.length > 0) {
                    console.log(`  Релевантные ячейки: ${relevantCells.length}`);
                    relevantCells.forEach((cell, i) => {
                        if (i < 3) {
                            console.log(`    ${i + 1}. "${cell.text}" ${cell.hasFormElements ? '(с элементами формы)' : ''}`);
                        }
                    });
                }
            }
        });

        console.log('\n✅ Анализ содержимого iframe завершен!');

    } catch (error) {
        console.log(`❌ Ошибка при анализе iframe: ${error.message}`);
    }
}

// Функция для тестирования взаимодействия с элементами в iframe
function testIframeElementInteraction(selector, action = 'click') {
    try {
        const iframes = document.querySelectorAll('iframe');
        if (iframes.length === 0) {
            console.log('❌ Iframe не найден');
            return false;
        }

        const iframe = iframes[0];
        if (!iframe.contentDocument) {
            console.log('❌ Нет доступа к содержимому iframe');
            return false;
        }

        const element = iframe.contentDocument.querySelector(selector);
        if (!element) {
            console.log(`❌ Элемент не найден в iframe: ${selector}`);
            return false;
        }

        const info = getElementInfo(element);
        console.log(`✅ Найден элемент в iframe: ${info.tagName} - ID: ${info.id}, Name: ${info.name}`);
        console.log(`   Видимый: ${info.isVisible}, Включен: ${info.isEnabled}, Только чтение: ${info.isReadOnly}`);

        if (action === 'click' && element.click) {
            console.log(`🖱️ Выполняем клик по элементу в iframe...`);
            element.click();
            console.log(`✅ Клик выполнен`);
        }

        return true;
    } catch (error) {
        console.log(`❌ Ошибка при взаимодействии с элементом в iframe: ${error.message}`);
        return false;
    }
}

// Запускаем анализ
analyzeIframeContent();

console.log('\n📝 ИНСТРУКЦИИ:');
console.log('1. Скопируйте код в консоль браузера');
console.log('2. Нажмите Enter для выполнения');
console.log('3. Изучите результаты анализа iframe');
console.log('4. Используйте testIframeElementInteraction("селектор") для тестирования элементов');
console.log('5. Скопируйте результаты и отправьте мне для создания Python скрипта');

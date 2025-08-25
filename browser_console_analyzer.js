// Скрипт для анализа страницы отчета в консоли браузера
// Скопируйте весь этот код в консоль браузера (F12 -> Console) и нажмите Enter

console.log('🔍 Начинаем анализ страницы отчета...');

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
        isReadOnly: element.readOnly || false
    };
}

// Функция для поиска элементов по тексту
function findElementsByText(searchText, tagName = null) {
    const xpath = tagName
        ? `//${tagName}[contains(text(), '${searchText}') or contains(@placeholder, '${searchText}') or contains(@title, '${searchText}')]`
        : `//*[contains(text(), '${searchText}') or contains(@placeholder, '${searchText}') or contains(@title, '${searchText}')]`;

    const elements = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    const result = [];

    for (let i = 0; i < elements.snapshotLength; i++) {
        result.push(elements.snapshotItem(i));
    }

    return result;
}

// Функция для поиска ближайших элементов формы
function findNearbyFormElements(labelElement, maxDistance = 3) {
    const formElements = [];

    // Ищем в следующих элементах
    let current = labelElement.nextElementSibling;
    for (let i = 0; i < maxDistance && current; i++) {
        if (current.tagName === 'INPUT' || current.tagName === 'SELECT' || current.tagName === 'TEXTAREA') {
            formElements.push({ element: current, direction: 'next', distance: i + 1 });
        }
        current = current.nextElementSibling;
    }

    // Ищем в предыдущих элементах
    current = labelElement.previousElementSibling;
    for (let i = 0; i < maxDistance && current; i++) {
        if (current.tagName === 'INPUT' || current.tagName === 'SELECT' || current.tagName === 'TEXTAREA') {
            formElements.push({ element: current, direction: 'previous', distance: i + 1 });
        }
        current = current.previousElementSibling;
    }

    // Ищем в родительском контейнере
    let parent = labelElement.parentElement;
    for (let i = 0; i < maxDistance && parent; i++) {
        const inputs = parent.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input !== labelElement) {
                formElements.push({ element: input, direction: 'parent', distance: i + 1 });
            }
        });
        parent = parent.parentElement;
    }

    return formElements;
}

// Основной анализ
function analyzeReportPage() {
    console.log('\n=== АНАЛИЗ СТРАНИЦЫ ОТЧЕТА ===\n');

    // 1. Анализируем все элементы формы
    console.log('📋 АНАЛИЗ ВСЕХ ЭЛЕМЕНТОВ ФОРМЫ:');
    const allInputs = document.querySelectorAll('input, select, textarea');
    console.log(`Найдено элементов формы: ${allInputs.length}`);

    allInputs.forEach((input, index) => {
        if (index < 20) { // Показываем первые 20
            const info = getElementInfo(input);
            console.log(`${index + 1}. ${input.tagName} - ID: ${info.id}, Name: ${info.name}, Type: ${info.type}`);
        }
    });

    if (allInputs.length > 20) {
        console.log(`... и еще ${allInputs.length - 20} элементов`);
    }

    // 2. Ищем поле "Период отчета"
    console.log('\n🔍 ПОИСК ПОЛЯ "ПЕРИОД ОТЧЕТА":');
    const periodLabels = findElementsByText('Период');
    console.log(`Найдено меток с текстом "Период": ${periodLabels.length}`);

    periodLabels.forEach((label, index) => {
        console.log(`${index + 1}. Метка: "${label.textContent.trim()}"`);
        const nearbyElements = findNearbyFormElements(label);
        if (nearbyElements.length > 0) {
            console.log(`   Ближайшие элементы формы:`);
            nearbyElements.forEach(nearby => {
                const info = getElementInfo(nearby.element);
                console.log(`   - ${nearby.element.tagName} (${nearby.direction}, расстояние: ${nearby.distance}): ID=${info.id}, Name=${info.name}`);
            });
        }
    });

    // 3. Ищем поля дат
    console.log('\n📅 ПОИСК ПОЛЕЙ ДАТ:');
    const dateLabels = findElementsByText('Дата');
    console.log(`Найдено меток с текстом "Дата": ${dateLabels.length}`);

    dateLabels.forEach((label, index) => {
        console.log(`${index + 1}. Метка: "${label.textContent.trim()}"`);
        const nearbyElements = findNearbyFormElements(label);
        if (nearbyElements.length > 0) {
            console.log(`   Ближайшие элементы формы:`);
            nearbyElements.forEach(nearby => {
                const info = getElementInfo(nearby.element);
                console.log(`   - ${nearby.element.tagName} (${nearby.direction}, расстояние: ${nearby.distance}): ID=${info.id}, Name=${info.name}, Type=${info.type}`);
            });
        }
    });

    // 4. Ищем поле "Причина обращения"
    console.log('\n🔍 ПОИСК ПОЛЯ "ПРИЧИНА ОБРАЩЕНИЯ":');
    const reasonLabels = findElementsByText('Причина');
    console.log(`Найдено меток с текстом "Причина": ${reasonLabels.length}`);

    reasonLabels.forEach((label, index) => {
        console.log(`${index + 1}. Метка: "${label.textContent.trim()}"`);
        const nearbyElements = findNearbyFormElements(label);
        if (nearbyElements.length > 0) {
            console.log(`   Ближайшие элементы формы:`);
            nearbyElements.forEach(nearby => {
                const info = getElementInfo(nearby.element);
                console.log(`   - ${nearby.element.tagName} (${nearby.direction}, расстояние: ${nearby.distance}): ID=${info.id}, Name=${info.name}`);
            });
        }
    });

    // 5. Ищем кнопки
    console.log('\n🔘 ПОИСК КНОПОК:');
    const buttons = document.querySelectorAll('button, input[type="submit"], input[type="button"]');
    console.log(`Найдено кнопок: ${buttons.length}`);

    buttons.forEach((button, index) => {
        if (index < 10) { // Показываем первые 10
            const info = getElementInfo(button);
            console.log(`${index + 1}. ${button.tagName} - ID: ${info.id}, Name: ${info.name}, Value: ${info.value}, Text: ${info.textContent}`);
        }
    });

    // 6. Анализируем структуру страницы
    console.log('\n🏗️ СТРУКТУРА СТРАНИЦЫ:');
    const tables = document.querySelectorAll('table');
    const forms = document.querySelectorAll('form');
    const divs = document.querySelectorAll('div');

    console.log(`Таблиц: ${tables.length}`);
    console.log(`Форм: ${forms.length}`);
    console.log(`Div блоков: ${divs.length}`);

    // 7. Ищем ReportViewer элементы
    console.log('\n📊 ПОИСК REPORTVIEWER ЭЛЕМЕНТОВ:');
    const reportElements = document.querySelectorAll('[class*="ReportViewer"], [id*="ReportViewer"]');
    console.log(`ReportViewer элементов: ${reportElements.length}`);

    reportElements.forEach((element, index) => {
        const info = getElementInfo(element);
        console.log(`${index + 1}. ${element.tagName} - ID: ${info.id}, Class: ${info.className}`);
    });

    // 8. Анализируем все select элементы
    console.log('\n📋 АНАЛИЗ ВЫПАДАЮЩИХ СПИСКОВ:');
    const selects = document.querySelectorAll('select');
    console.log(`Выпадающих списков: ${selects.length}`);

    selects.forEach((select, index) => {
        const info = getElementInfo(select);
        const options = select.querySelectorAll('option');
        console.log(`${index + 1}. Select - ID: ${info.id}, Name: ${info.name}, Опций: ${options.length}`);

        if (options.length <= 10) {
            options.forEach((option, optIndex) => {
                console.log(`   ${optIndex + 1}. ${option.text} (value: ${option.value})`);
            });
        } else {
            console.log(`   Первые 5 опций:`);
            for (let i = 0; i < 5; i++) {
                console.log(`   ${i + 1}. ${options[i].text} (value: ${options[i].value})`);
            }
            console.log(`   ... и еще ${options.length - 5} опций`);
        }
    });

    // 9. Анализируем все input элементы
    console.log('\n✏️ АНАЛИЗ ПОЛЕЙ ВВОДА:');
    const inputs = document.querySelectorAll('input');
    console.log(`Полей ввода: ${inputs.length}`);

    const inputTypes = {};
    inputs.forEach(input => {
        const type = input.type || 'text';
        inputTypes[type] = (inputTypes[type] || 0) + 1;
    });

    Object.entries(inputTypes).forEach(([type, count]) => {
        console.log(`   ${type}: ${count}`);
    });

    // 10. Ищем скрытые поля
    console.log('\n🔒 СКРЫТЫЕ ПОЛЯ:');
    const hiddenInputs = document.querySelectorAll('input[type="hidden"]');
    console.log(`Скрытых полей: ${hiddenInputs.length}`);

    hiddenInputs.forEach((input, index) => {
        if (index < 10) {
            const info = getElementInfo(input);
            console.log(`${index + 1}. Hidden - ID: ${info.id}, Name: ${info.name}, Value: ${info.value}`);
        }
    });

    if (hiddenInputs.length > 10) {
        console.log(`... и еще ${hiddenInputs.length - 10} скрытых полей`);
    }

    console.log('\n✅ Анализ завершен!');
    console.log('\n💡 РЕКОМЕНДАЦИИ:');
    console.log('1. Обратите внимание на найденные элементы формы');
    console.log('2. Проверьте, какие поля заблокированы до выбора периода');
    console.log('3. Определите правильные селекторы для автоматизации');
    console.log('4. Проверьте, есть ли JavaScript события, блокирующие поля');
}

// Запускаем анализ
analyzeReportPage();

// Дополнительная функция для тестирования взаимодействия
function testElementInteraction(selector, action = 'click') {
    try {
        const element = document.querySelector(selector);
        if (!element) {
            console.log(`❌ Элемент не найден: ${selector}`);
            return false;
        }

        const info = getElementInfo(element);
        console.log(`✅ Найден элемент: ${info.tagName} - ID: ${info.id}, Name: ${info.name}`);
        console.log(`   Видимый: ${info.isVisible}, Включен: ${info.isEnabled}, Только чтение: ${info.isReadOnly}`);

        if (action === 'click' && element.click) {
            console.log(`🖱️ Выполняем клик по элементу...`);
            element.click();
            console.log(`✅ Клик выполнен`);
        }

        return true;
    } catch (error) {
        console.log(`❌ Ошибка при взаимодействии: ${error.message}`);
        return false;
    }
}

// Функция для поиска элементов по различным критериям
function findFormElementsAdvanced() {
    console.log('\n🔍 ПРОДВИНУТЫЙ ПОИСК ЭЛЕМЕНТОВ ФОРМЫ:');

    // Ищем по ID
    const idPatterns = ['period', 'Period', 'date', 'Date', 'start', 'Start', 'end', 'End', 'reason', 'Reason'];
    idPatterns.forEach(pattern => {
        const elements = document.querySelectorAll(`[id*="${pattern}"]`);
        if (elements.length > 0) {
            console.log(`\nЭлементы с ID содержащим "${pattern}":`);
            elements.forEach((el, index) => {
                const info = getElementInfo(el);
                console.log(`  ${index + 1}. ${el.tagName} - ID: ${info.id}, Name: ${info.name}, Type: ${info.type}`);
            });
        }
    });

    // Ищем по name
    const namePatterns = ['period', 'Period', 'date', 'Date', 'start', 'Start', 'end', 'End', 'reason', 'Reason'];
    namePatterns.forEach(pattern => {
        const elements = document.querySelectorAll(`[name*="${pattern}"]`);
        if (elements.length > 0) {
            console.log(`\nЭлементы с name содержащим "${pattern}":`);
            elements.forEach((el, index) => {
                const info = getElementInfo(el);
                console.log(`  ${index + 1}. ${el.tagName} - ID: ${info.id}, Name: ${info.name}, Type: ${info.type}`);
            });
        }
    });
}

// Запускаем дополнительный поиск
setTimeout(findFormElementsAdvanced, 1000);

console.log('\n📝 ИНСТРУКЦИИ ПО ИСПОЛЬЗОВАНИЮ:');
console.log('1. Скопируйте весь код в консоль браузера (F12 -> Console)');
console.log('2. Нажмите Enter для выполнения');
console.log('3. Изучите результаты анализа');
console.log('4. Используйте testElementInteraction("селектор") для тестирования элементов');
console.log('5. Скопируйте результаты и отправьте мне для корректировки скрипта');

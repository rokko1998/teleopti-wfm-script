// Продвинутый анализатор страницы отчета для поиска элементов в iframe'ах и динамическом контенте
// Скопируйте весь этот код в консоль браузера (F12 -> Console) и нажмите Enter

console.log('🔍 Запуск продвинутого анализатора страницы...');

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
        src: element.src || 'Нет src',
        href: element.href || 'Нет href'
    };
}

// Функция для анализа iframe'ов
function analyzeIframes() {
    console.log('\n🖼️ АНАЛИЗ IFRAME ЭЛЕМЕНТОВ:');
    const iframes = document.querySelectorAll('iframe');
    console.log(`Найдено iframe'ов: ${iframes.length}`);

    iframes.forEach((iframe, index) => {
        const info = getElementInfo(iframe);
        console.log(`${index + 1}. Iframe - ID: ${info.id}, Name: ${info.name}, Src: ${info.src}`);

        try {
            // Пытаемся получить доступ к содержимому iframe
            if (iframe.contentDocument) {
                const iframeInputs = iframe.contentDocument.querySelectorAll('input, select, textarea');
                const iframeButtons = iframe.contentDocument.querySelectorAll('button, input[type="submit"]');
                console.log(`   Элементов формы в iframe: ${iframeInputs.length}`);
                console.log(`   Кнопок в iframe: ${iframeButtons.length}`);

                if (iframeInputs.length > 0) {
                    console.log(`   Первые элементы формы в iframe:`);
                    iframeInputs.forEach((input, i) => {
                        if (i < 5) {
                            const inputInfo = getElementInfo(input);
                            console.log(`     ${i + 1}. ${input.tagName} - ID: ${inputInfo.id}, Name: ${inputInfo.name}, Type: ${inputInfo.type}`);
                        }
                    });
                }
            } else {
                console.log(`   ⚠️ Нет доступа к содержимому iframe (возможно, cross-origin)`);
            }
        } catch (error) {
            console.log(`   ❌ Ошибка доступа к iframe: ${error.message}`);
        }
    });
}

// Функция для анализа embed и object элементов
function analyzeEmbedElements() {
    console.log('\n🔌 АНАЛИЗ EMBED И OBJECT ЭЛЕМЕНТОВ:');
    const embeds = document.querySelectorAll('embed, object');
    console.log(`Найдено embed/object элементов: ${embeds.length}`);

    embeds.forEach((embed, index) => {
        const info = getElementInfo(embed);
        console.log(`${index + 1}. ${embed.tagName} - ID: ${info.id}, Name: ${info.name}, Src: ${info.src}`);
    });
}

// Функция для поиска элементов по всему документу (включая shadow DOM)
function findAllFormElements() {
    console.log('\n🔍 ПОИСК ВСЕХ ЭЛЕМЕНТОВ ФОРМЫ (ВКЛЮЧАЯ SHADOW DOM):');

    // Ищем по всему документу
    const allInputs = document.querySelectorAll('input, select, textarea, button');
    console.log(`Всего элементов формы в основном документе: ${allInputs.length}`);

    // Ищем в shadow DOM
    let shadowElements = [];
    function findInShadowDOM(root) {
        if (root.shadowRoot) {
            const shadowInputs = root.shadowRoot.querySelectorAll('input, select, textarea, button');
            shadowElements = shadowElements.concat(Array.from(shadowInputs));

            // Рекурсивно ищем в дочерних элементах
            const shadowChildren = root.shadowRoot.querySelectorAll('*');
            shadowChildren.forEach(child => findInShadowDOM(child));
        }
    }

    // Ищем shadow DOM во всех элементах
    const allElements = document.querySelectorAll('*');
    allElements.forEach(element => findInShadowDOM(element));

    console.log(`Элементов формы в shadow DOM: ${shadowElements.length}`);

    // Объединяем результаты
    const totalElements = allInputs.length + shadowElements.length;
    console.log(`Общее количество элементов формы: ${totalElements}`);

    return { main: allInputs, shadow: shadowElements, total: totalElements };
}

// Функция для поиска элементов по различным селекторам
function findElementsByMultipleSelectors() {
    console.log('\n🎯 ПОИСК ПО РАЗЛИЧНЫМ СЕЛЕКТОРАМ:');

    const selectors = [
        // По классам
        '.form-control', '.form-group', '.input-group', '.form-element',
        // По атрибутам
        '[data-field]', '[data-input]', '[data-form]',
        // По ролям
        '[role="textbox"]', '[role="combobox"]', '[role="button"]',
        // По aria атрибутам
        '[aria-label*="период"]', '[aria-label*="дата"]', '[aria-label*="причина"]',
        '[aria-label*="period"]', '[aria-label*="date"]', '[aria-label*="reason"]',
        // По placeholder
        '[placeholder*="период"]', '[placeholder*="дата"]', '[placeholder*="причина"]',
        '[placeholder*="period"]', '[placeholder*="date"]', '[placeholder*="reason"]',
        // По title
        '[title*="период"]', '[title*="дата"]', '[title*="причина"]',
        '[title*="period"]', '[title*="date"]', '[title*="reason"]'
    ];

    selectors.forEach(selector => {
        try {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                console.log(`\nСелектор "${selector}": найдено ${elements.length} элементов`);
                elements.forEach((el, index) => {
                    if (index < 3) { // Показываем первые 3
                        const info = getElementInfo(el);
                        console.log(`  ${index + 1}. ${el.tagName} - ID: ${info.id}, Name: ${info.name}, Class: ${info.className}`);
                    }
                });
                if (elements.length > 3) {
                    console.log(`  ... и еще ${elements.length - 3} элементов`);
                }
            }
        } catch (error) {
            // Игнорируем ошибки селекторов
        }
    });
}

// Функция для анализа структуры DOM
function analyzeDOMStructure() {
    console.log('\n🏗️ АНАЛИЗ СТРУКТУРЫ DOM:');

    // Ищем контейнеры с формами
    const formContainers = document.querySelectorAll('div, section, article, main');
    console.log(`Контейнеров div/section/article/main: ${formContainers.length}`);

    // Анализируем первые 10 контейнеров
    formContainers.forEach((container, index) => {
        if (index < 10) {
            const inputs = container.querySelectorAll('input, select, textarea');
            const buttons = container.querySelectorAll('button, input[type="submit"]');
            const labels = container.querySelectorAll('label, span, div');

            if (inputs.length > 0 || buttons.length > 0) {
                console.log(`\nКонтейнер ${index + 1}:`);
                console.log(`  Элементов формы: ${inputs.length}`);
                console.log(`  Кнопок: ${buttons.length}`);
                console.log(`  Текстовых элементов: ${labels.length}`);

                // Ищем текст с ключевыми словами
                const textContent = container.textContent || '';
                const keywords = ['период', 'дата', 'причина', 'отчет', 'period', 'date', 'reason', 'report'];
                const foundKeywords = keywords.filter(keyword =>
                    textContent.toLowerCase().includes(keyword.toLowerCase())
                );

                if (foundKeywords.length > 0) {
                    console.log(`  Найденные ключевые слова: ${foundKeywords.join(', ')}`);
                }
            }
        }
    });
}

// Функция для ожидания загрузки динамического контента
function waitForDynamicContent() {
    console.log('\n⏳ ОЖИДАНИЕ ЗАГРУЗКИ ДИНАМИЧЕСКОГО КОНТЕНТА...');

    return new Promise((resolve) => {
        let attempts = 0;
        const maxAttempts = 10;

        const checkContent = () => {
            attempts++;
            const currentInputs = document.querySelectorAll('input, select, textarea').length;
            const currentButtons = document.querySelectorAll('button, input[type="submit"]').length;

            console.log(`Попытка ${attempts}: найдено ${currentInputs} полей ввода, ${currentButtons} кнопок`);

            if (currentInputs > 2 || currentButtons > 1) {
                console.log('✅ Динамический контент загружен!');
                resolve(true);
            } else if (attempts >= maxAttempts) {
                console.log('⚠️ Таймаут ожидания динамического контента');
                resolve(false);
            } else {
                setTimeout(checkContent, 1000);
            }
        };

        checkContent();
    });
}

// Функция для поиска элементов по тексту в родительских контейнерах
function findElementsByTextInContainers() {
    console.log('\n🔍 ПОИСК ЭЛЕМЕНТОВ ПО ТЕКСТУ В КОНТЕЙНЕРАХ:');

    const keywords = ['период', 'дата', 'причина', 'отчет', 'period', 'date', 'reason', 'report'];

    keywords.forEach(keyword => {
        const elements = document.querySelectorAll('*');
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
}

// Основная функция анализа
async function advancedPageAnalysis() {
    console.log('\n🚀 ЗАПУСК ПРОДВИНУТОГО АНАЛИЗА СТРАНИЦЫ...\n');

    // 1. Анализируем iframe'ы
    analyzeIframes();

    // 2. Анализируем embed элементы
    analyzeEmbedElements();

    // 3. Ищем элементы по различным селекторам
    findElementsByMultipleSelectors();

    // 4. Анализируем структуру DOM
    analyzeDOMStructure();

    // 5. Ищем элементы по тексту в контейнерах
    findElementsByTextInContainers();

    // 6. Ищем все элементы формы (включая shadow DOM)
    const formElements = findAllFormElements();

    // 7. Ждем загрузки динамического контента
    console.log('\n⏳ Ждем загрузки динамического контента...');
    const dynamicContentLoaded = await waitForDynamicContent();

    if (dynamicContentLoaded) {
        console.log('\n🔄 Повторный анализ после загрузки динамического контента...');

        // Повторяем анализ
        const newFormElements = findAllFormElements();
        console.log(`\n📊 СРАВНЕНИЕ РЕЗУЛЬТАТОВ:`);
        console.log(`До ожидания: ${formElements.total} элементов`);
        console.log(`После ожидания: ${newFormElements.total} элементов`);

        if (newFormElements.total > formElements.total) {
            console.log('✅ Найдено новых элементов!');
        }
    }

    console.log('\n✅ Продвинутый анализ завершен!');
    console.log('\n💡 РЕКОМЕНДАЦИИ:');
    console.log('1. Проверьте, есть ли iframe\'ы с формами');
    console.log('2. Возможно, форма загружается через AJAX/JavaScript');
    console.log('3. Проверьте, есть ли ошибки в консоли браузера');
    console.log('4. Попробуйте обновить страницу и подождать');
}

// Запускаем анализ
advancedPageAnalysis();

// Дополнительные функции для тестирования
function testIframeAccess() {
    console.log('\n🧪 ТЕСТИРОВАНИЕ ДОСТУПА К IFRAME:');
    const iframes = document.querySelectorAll('iframe');

    iframes.forEach((iframe, index) => {
        console.log(`\nIframe ${index + 1}:`);
        try {
            if (iframe.contentDocument) {
                console.log('✅ Доступ к содержимому iframe есть');
                const inputs = iframe.contentDocument.querySelectorAll('input, select, textarea');
                console.log(`   Элементов формы: ${inputs.length}`);
            } else {
                console.log('❌ Нет доступа к содержимому iframe');
            }
        } catch (error) {
            console.log(`❌ Ошибка: ${error.message}`);
        }
    });
}

// Запускаем тест iframe через 2 секунды
setTimeout(testIframeAccess, 2000);

console.log('\n📝 ИНСТРУКЦИИ:');
console.log('1. Скопируйте код в консоль браузера');
console.log('2. Нажмите Enter для выполнения');
console.log('3. Дождитесь завершения анализа');
console.log('4. Скопируйте результаты и отправьте мне');

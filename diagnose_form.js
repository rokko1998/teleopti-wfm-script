// Диагностический скрипт для анализа полей формы отчета
// Скопируйте в консоль браузера и нажмите Enter

console.log('🔍 ДИАГНОСТИКА ПОЛЕЙ ФОРМЫ ОТЧЕТА');
console.log('=====================================');

try {
    // Получаем доступ к iframe
    const iframe = document.querySelector('iframe.viewer') || document.querySelector('iframe');
    if (!iframe) {
        console.log('❌ Iframe не найден');
        console.log('Проверьте, что страница полностью загружена');
        return;
    }

    console.log('✅ Iframe найден');
    const doc = iframe.contentDocument;

    if (!doc) {
        console.log('❌ Нет доступа к содержимому iframe');
        console.log('Возможно, iframe еще не загружен или заблокирован CORS');
        return;
    }

    console.log('✅ Доступ к содержимому iframe получен');

    // Анализируем все поля формы
    console.log('\n📋 АНАЛИЗ ПОЛЕЙ ФОРМЫ:');
    console.log('========================');

    // 1. Период отчета
    const periodField = doc.getElementById('ReportViewerControl_ctl04_ctl03_ddValue');
    if (periodField) {
        console.log('\n📊 ПОЛЕ "ПЕРИОД ОТЧЕТА":');
        console.log('   ID:', periodField.id);
        console.log('   Тип:', periodField.type);
        console.log('   Тег:', periodField.tagName);
        console.log('   Заблокировано:', periodField.disabled);
        console.log('   Классы:', periodField.className);
        console.log('   Текущее значение:', periodField.value);
        console.log('   Текущий текст:', periodField.options?.[periodField.selectedIndex]?.text);

        if (periodField.options) {
            console.log('   Доступные опции:');
            for (let i = 0; i < periodField.options.length; i++) {
                const option = periodField.options[i];
                console.log(`     ${i}: value="${option.value}", text="${option.text}"`);
            }
        }

        console.log('   Selenium селектор:', `By.ID("${periodField.id}")`);
        console.log('   Selenium взаимодействие:', 'Select(driver.find_element(By.ID("' + periodField.id + '"))).select_by_value("900")');
    } else {
        console.log('❌ Поле "Период отчета" не найдено');
    }

    // 2. Дата начала
    const startDateField = doc.getElementById('ReportViewerControl_ctl04_ctl05_txtValue');
    if (startDateField) {
        console.log('\n📅 ПОЛЕ "ДАТА НАЧАЛА":');
        console.log('   ID:', startDateField.id);
        console.log('   Тип:', startDateField.type);
        console.log('   Тег:', startDateField.tagName);
        console.log('   Заблокировано:', startDateField.disabled);
        console.log('   Классы:', startDateField.className);
        console.log('   Readonly:', startDateField.readOnly);
        console.log('   Текущее значение:', startDateField.value);
        console.log('   Placeholder:', startDateField.placeholder);
        console.log('   Maxlength:', startDateField.maxLength);

        console.log('   Selenium селектор:', `By.ID("${startDateField.id}")`);
        console.log('   Selenium взаимодействие:', 'driver.find_element(By.ID("' + startDateField.id + '")).clear(); driver.find_element(By.ID("' + startDateField.id + '")).send_keys("01.08.2025")');
    } else {
        console.log('❌ Поле "Дата начала" не найдено');
    }

    // 3. Дата окончания
    const endDateField = doc.getElementById('ReportViewerControl_ctl04_ctl07_txtValue');
    if (endDateField) {
        console.log('\n📅 ПОЛЕ "ДАТА ОКОНЧАНИЯ":');
        console.log('   ID:', endDateField.id);
        console.log('   Тип:', endDateField.type);
        console.log('   Тег:', endDateField.tagName);
        console.log('   Заблокировано:', endDateField.disabled);
        console.log('   Классы:', endDateField.className);
        console.log('   Readonly:', endDateField.readOnly);
        console.log('   Текущее значение:', endDateField.value);
        console.log('   Placeholder:', endDateField.placeholder);
        console.log('   Maxlength:', endDateField.maxLength);

        console.log('   Selenium селектор:', `By.ID("${endDateField.id}")`);
        console.log('   Selenium взаимодействие:', 'driver.find_element(By.ID("' + endDateField.id + '")).clear(); driver.find_element(By.ID("' + endDateField.id + '")).send_keys("02.08.2025")');
    } else {
        console.log('❌ Поле "Дата окончания" не найдено');
    }

    // 4. Причина обращения
    const reasonField = doc.getElementById('ReportViewerControl_ctl04_ctl09_txtValue');
    if (reasonField) {
        console.log('\n🔍 ПОЛЕ "ПРИЧИНА ОБРАЩЕНИЯ":');
        console.log('   ID:', reasonField.id);
        console.log('   Тип:', reasonField.type);
        console.log('   Тег:', reasonField.tagName);
        console.log('   Заблокировано:', reasonField.disabled);
        console.log('   Классы:', reasonField.className);
        console.log('   Readonly:', reasonField.readOnly);
        console.log('   Текущее значение:', reasonField.value);
        console.log('   Placeholder:', reasonField.placeholder);
        console.log('   Maxlength:', reasonField.maxLength);

        console.log('   Selenium селектор:', `By.ID("${reasonField.id}")`);
        console.log('   Selenium взаимодействие:', 'driver.find_element(By.ID("' + reasonField.id + '")).clear(); driver.find_element(By.ID("' + reasonField.id + '")).send_keys("Низкая скорость в 3G/4G")');
    } else {
        console.log('❌ Поле "Причина обращения" не найдено');
    }

    // 5. Кнопка отправки
    const submitButton = doc.getElementById('ReportViewerControl_ctl04_ctl00');
    if (submitButton) {
        console.log('\n🚀 КНОПКА "ОТПРАВИТЬ":');
        console.log('   ID:', submitButton.id);
        console.log('   Тип:', submitButton.type);
        console.log('   Тег:', submitButton.tagName);
        console.log('   Заблокировано:', submitButton.disabled);
        console.log('   Классы:', submitButton.className);
        console.log('   Текст:', submitButton.textContent);
        console.log('   Value:', submitButton.value);

        console.log('   Selenium селектор:', `By.ID("${submitButton.id}")`);
        console.log('   Selenium взаимодействие:', 'driver.find_element(By.ID("' + submitButton.id + '")).click()');
    } else {
        console.log('❌ Кнопка "Отправить" не найдена');
    }

    // 6. Ищем все input поля для дополнительного анализа
    console.log('\n🔍 ДОПОЛНИТЕЛЬНЫЕ ПОЛЯ:');
    console.log('========================');

    const allInputs = doc.querySelectorAll('input, select, textarea');
    console.log(`   Найдено полей: ${allInputs.length}`);

    allInputs.forEach((input, index) => {
        if (input.id && input.id.includes('ReportViewerControl')) {
            console.log(`   ${index + 1}. ID: ${input.id}`);
            console.log(`      Тип: ${input.type || input.tagName}`);
            console.log(`      Значение: ${input.value}`);
            console.log(`      Заблокировано: ${input.disabled}`);
            console.log(`      Классы: ${input.className}`);
            console.log(`      Selenium: By.ID("${input.id}")`);
            console.log('');
        }
    });

    // 7. Анализ состояния блокировки
    console.log('\n🔒 АНАЛИЗ СОСТОЯНИЯ БЛОКИРОВКИ:');
    console.log('==================================');

    if (startDateField) {
        const startBlocked = startDateField.disabled || startDateField.className.includes('aspNetDisabled');
        console.log(`   Дата начала заблокирована: ${startBlocked}`);
        if (startBlocked) {
            console.log('   🔓 Для разблокировки в Selenium:');
            console.log('      driver.execute_script("arguments[0].removeAttribute(\'disabled\');", element)');
            console.log('      driver.execute_script("arguments[0].classList.remove(\'aspNetDisabled\');", element)');
        }
    }

    if (endDateField) {
        const endBlocked = endDateField.disabled || endDateField.className.includes('aspNetDisabled');
        console.log(`   Дата окончания заблокирована: ${endBlocked}`);
    }

    if (reasonField) {
        const reasonBlocked = reasonField.disabled || reasonField.className.includes('aspNetDisabled');
        console.log(`   Причина обращения заблокирована: ${reasonBlocked}`);
    }

    // 8. Рекомендации по Selenium
    console.log('\n💡 РЕКОМЕНДАЦИИ ПО SELENIUM:');
    console.log('==============================');
    console.log('1. Всегда переключайтесь на iframe: driver.switch_to.frame(iframe)');
    console.log('2. После работы возвращайтесь: driver.switch_to.default_content()');
    console.log('3. Для заблокированных полей используйте JavaScript:');
    console.log('   driver.execute_script("arguments[0].removeAttribute(\'disabled\');", element)');
    console.log('4. Ждите готовности элементов: WebDriverWait(driver, 10).until(EC.element_to_be_clickable(...))');
    console.log('5. Очищайте поля перед вводом: element.clear()');

} catch (error) {
    console.error('❌ Ошибка при диагностике:', error);
}

console.log('\n📝 ИНСТРУКЦИИ:');
console.log('1. Скопируйте код в консоль браузера');
console.log('2. Нажмите Enter для выполнения');
console.log('3. Изучите результаты диагностики');
console.log('4. Скопируйте результаты и отправьте мне');

// Тестовый скрипт для проверки значений в выпадающем списке периода отчета
// Скопируйте в консоль браузера и нажмите Enter

console.log('🔍 Тестирование значений периода отчета...');

try {
    // Получаем доступ к iframe
    const iframe = document.querySelector('iframe.viewer') || document.querySelector('iframe');
    if (!iframe) {
        console.log('❌ Iframe не найден');
        console.log('Проверьте, что страница полностью загружена');
        console.log('Попробуйте подождать еще немного и запустить скрипт снова');
        console.log('Скрипт завершен');
        return;
    }

    console.log('✅ Iframe найден:', iframe.src);

    const doc = iframe.contentDocument;
    if (!doc) {
        console.log('❌ Нет доступа к содержимому iframe');
        console.log('Возможно, iframe еще не загружен или заблокирован CORS');
        console.log('Попробуйте подождать еще немного и запустить скрипт снова');
        console.log('Скрипт завершен');
        return;
    }

    console.log('✅ Доступ к содержимому iframe получен');

    // Ищем выпадающий список периода отчета
    const periodSelect = doc.getElementById('ReportViewerControl_ctl04_ctl03_ddValue');
    if (!periodSelect) {
        console.log('❌ Выпадающий список периода отчета не найден');
        console.log('Проверьте ID элемента или дождитесь полной загрузки страницы');
        console.log('Попробуйте подождать еще немного и запустить скрипт снова');
        console.log('Скрипт завершен');
        return;
    }

    console.log('✅ Выпадающий список периода отчета найден');
    console.log('📋 Текущее значение:', periodSelect.value);
    console.log('📋 Текущий текст:', periodSelect.options[periodSelect.selectedIndex]?.text);

    // Анализируем все доступные опции
    console.log('\n📋 Все доступные опции:');
    const options = periodSelect.options;
    for (let i = 0; i < options.length; i++) {
        const option = options[i];
        console.log(`  ${i}: value="${option.value}", text="${option.text}"`);
    }

    // Тестируем установку значения "900" (Произвольный)
    console.log('\n🧪 Тестируем установку значения "900"...');

    // Сохраняем текущее значение
    const originalValue = periodSelect.value;
    console.log('📋 Исходное значение:', originalValue);

    // Устанавливаем новое значение
    periodSelect.value = '900';
    console.log('📋 Новое значение после установки:', periodSelect.value);

    // Проверяем, изменился ли выбранный текст
    const selectedText = periodSelect.options[periodSelect.selectedIndex]?.text;
    console.log('📋 Выбранный текст после изменения:', selectedText);

    // Проверяем, разблокировались ли поля дат
    console.log('\n🔓 Проверяем разблокировку полей дат...');

    const startDateField = doc.getElementById('ReportViewerControl_ctl04_ctl05_txtValue');
    if (startDateField) {
        console.log('📅 Поле "Дата начала":');
        console.log('   ID:', startDateField.id);
        console.log('   Заблокировано:', startDateField.disabled);
        console.log('   Класс:', startDateField.className);
        console.log('   Только чтение:', startDateField.readOnly);
    } else {
        console.log('❌ Поле "Дата начала" не найдено');
    }

    const endDateField = doc.getElementById('ReportViewerControl_ctl04_ctl07_txtValue');
    if (endDateField) {
        console.log('📅 Поле "Дата окончания":');
        console.log('   ID:', endDateField.id);
        console.log('   Заблокировано:', endDateField.disabled);
        console.log('   Класс:', endDateField.className);
        console.log('   Только чтение:', endDateField.readOnly);
    } else {
        console.log('❌ Поле "Дата окончания" не найдено');
    }

    const reasonField = doc.getElementById('ReportViewerControl_ctl04_ctl09_txtValue');
    if (reasonField) {
        console.log('🔍 Поле "Причина обращения":');
        console.log('   ID:', reasonField.id);
        console.log('   Заблокировано:', reasonField.disabled);
        console.log('   Класс:', reasonField.className);
        console.log('   Только чтение:', reasonField.readOnly);
    } else {
        console.log('❌ Поле "Причина обращения" не найдено');
    }

    // Восстанавливаем исходное значение
    periodSelect.value = originalValue;
    console.log('\n🔄 Исходное значение восстановлено:', periodSelect.value);

    console.log('\n✅ Тестирование завершено!');

} catch (error) {
    console.error('❌ Ошибка при тестировании:', error);
}

console.log('\n📝 Инструкции:');
console.log('1. Скопируйте код в консоль браузера');
console.log('2. Нажмите Enter для выполнения');
console.log('3. Изучите результаты тестирования');
console.log('4. Скопируйте результаты и отправьте мне');

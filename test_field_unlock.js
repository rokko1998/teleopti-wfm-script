// Тестовый скрипт для проверки разблокировки полей после выбора периода
// Скопируйте в консоль браузера и нажмите Enter

console.log('🔍 Тестирование разблокировки полей...');

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

    console.log('✅ Iframe найден');

    const doc = iframe.contentDocument;
    if (!doc) {
        console.log('❌ Нет доступа к содержимому iframe');
        console.log('Возможно, iframe еще не загружен или заблокирован CORS');
        console.log('Попробуйте подождать еще немного и запустить скрипт снова');
        console.log('Скрипт завершен');
        return;
    }

    console.log('✅ Доступ к содержимому iframe получен');

    // 1. Проверяем исходное состояние полей
    console.log('\n📋 ИСХОДНОЕ СОСТОЯНИЕ ПОЛЕЙ:');

    const startDateField = doc.getElementById('ReportViewerControl_ctl04_ctl05_txtValue');
    const endDateField = doc.getElementById('ReportViewerControl_ctl04_ctl07_txtValue');
    const reasonField = doc.getElementById('ReportViewerControl_ctl04_ctl09_txtValue');

    if (startDateField) {
        console.log('📅 Поле "Дата начала":');
        console.log('   ID:', startDateField.id);
        console.log('   Заблокировано:', startDateField.disabled);
        console.log('   Класс:', startDateField.className);
        console.log('   Readonly:', startDateField.readOnly);
        console.log('   Значение:', startDateField.value);
    } else {
        console.log('❌ Поле "Дата начала" не найдено');
    }

    if (endDateField) {
        console.log('📅 Поле "Дата окончания":');
        console.log('   ID:', endDateField.id);
        console.log('   Заблокировано:', endDateField.disabled);
        console.log('   Класс:', endDateField.className);
        console.log('   Readonly:', endDateField.readOnly);
        console.log('   Значение:', endDateField.value);
    } else {
        console.log('❌ Поле "Дата окончания" не найдено');
    }

    if (reasonField) {
        console.log('🔍 Поле "Причина обращения":');
        console.log('   ID:', reasonField.id);
        console.log('   Заблокировано:', reasonField.disabled);
        console.log('   Класс:', reasonField.className);
        console.log('   Readonly:', reasonField.readOnly);
        console.log('   Значение:', reasonField.value);
    } else {
        console.log('❌ Поле "Причина обращения" не найдено');
    }

    // 2. Выбираем период "Произвольный"
    console.log('\n🔄 ВЫБИРАЕМ ПЕРИОД "ПРОИЗВОЛЬНЫЙ"...');

    const periodSelect = doc.getElementById('ReportViewerControl_ctl04_ctl03_ddValue');
    if (!periodSelect) {
        console.log('❌ Выпадающий список периода не найден');
        console.log('Проверьте ID элемента или дождитесь полной загрузки страницы');
        console.log('Попробуйте подождать еще немного и запустить скрипт снова');
        console.log('Скрипт завершен');
        return;
    }

    console.log('📋 Текущий период:', periodSelect.value, '(', periodSelect.options[periodSelect.selectedIndex]?.text, ')');

    // Устанавливаем "Произвольный"
    periodSelect.value = '900';
    console.log('📋 Установлен период:', periodSelect.value, '(', periodSelect.options[periodSelect.selectedIndex]?.text, ')');

    // 3. Ждем и проверяем разблокировку
    console.log('\n⏳ ЖДЕМ РАЗБЛОКИРОВКИ ПОЛЕЙ...');

    let attempts = 0;
    const maxAttempts = 10;

    const checkUnlock = () => {
        attempts++;
        console.log(`\n🔍 Попытка ${attempts}: проверяем разблокировку...`);

        if (startDateField) {
            const startUnlocked = !startDateField.disabled && !startDateField.className.includes('aspNetDisabled');
            console.log('📅 Дата начала разблокирована:', startUnlocked);
            console.log('   Заблокировано:', startDateField.disabled);
            console.log('   Класс:', startDateField.className);
        }

        if (endDateField) {
            const endUnlocked = !endDateField.disabled && !endDateField.className.includes('aspNetDisabled');
            console.log('📅 Дата окончания разблокирована:', endUnlocked);
            console.log('   Заблокировано:', endDateField.disabled);
            console.log('   Класс:', endDateField.className);
        }

        if (reasonField) {
            const reasonUnlocked = !reasonField.disabled && !reasonField.className.includes('aspNetDisabled');
            console.log('🔍 Причина обращения разблокирована:', reasonUnlocked);
            console.log('   Заблокировано:', reasonField.disabled);
            console.log('   Класс:', reasonField.className);
        }

        // Проверяем, все ли поля разблокированы
        const allUnlocked = (!startDateField || (!startDateField.disabled && !startDateField.className.includes('aspNetDisabled'))) &&
                           (!endDateField || (!endDateField.disabled && !endDateField.className.includes('aspNetDisabled'))) &&
                           (!reasonField || (!reasonField.disabled && !reasonField.className.includes('aspNetDisabled')));

        if (allUnlocked) {
            console.log('✅ Все поля разблокированы!');
            return true;
        }

        if (attempts >= maxAttempts) {
            console.log('⚠️ Таймаут ожидания разблокировки');
            return false;
        }

        // Продолжаем проверку
        setTimeout(checkUnlock, 2000);
    };

    // Запускаем проверку
    setTimeout(checkUnlock, 2000);

    // 4. Пробуем принудительно разблокировать поля
    console.log('\n🔧 ПРОБУЕМ ПРИНУДИТЕЛЬНО РАЗБЛОКИРОВАТЬ ПОЛЯ...');

    setTimeout(() => {
        if (startDateField) {
            console.log('🔓 Принудительно разблокируем поле "Дата начала"...');

            // Убираем атрибут disabled
            startDateField.removeAttribute('disabled');

            // Убираем классы блокировки
            startDateField.className = startDateField.className.replace('aspNetDisabled', '').replace('DisabledTextBox', '').trim();

            // Устанавливаем значение
            startDateField.value = '01.01.2025';

            console.log('📅 Поле "Дата начала" после принудительной разблокировки:');
            console.log('   Заблокировано:', startDateField.disabled);
            console.log('   Класс:', startDateField.className);
            console.log('   Значение:', startDateField.value);
        }

        if (endDateField) {
            console.log('🔓 Принудительно разблокируем поле "Дата окончания"...');

            endDateField.removeAttribute('disabled');
            endDateField.className = endDateField.className.replace('aspNetDisabled', '').replace('DisabledTextBox', '').trim();
            endDateField.value = '02.01.2025';

            console.log('📅 Поле "Дата окончания" после принудительной разблокировки:');
            console.log('   Заблокировано:', endDateField.disabled);
            console.log('   Класс:', endDateField.className);
            console.log('   Значение:', endDateField.value);
        }

        if (reasonField) {
            console.log('🔓 Принудительно разблокируем поле "Причина обращения"...');

            reasonField.removeAttribute('disabled');
            reasonField.className = reasonField.className.replace('aspNetDisabled', '').replace('DisabledTextBox', '').trim();
            reasonField.value = 'Низкая скорость в 3G/4G';

            console.log('🔍 Поле "Причина обращения" после принудительной разблокировки:');
            console.log('   Заблокировано:', reasonField.disabled);
            console.log('   Класс:', reasonField.className);
            console.log('   Значение:', reasonField.value);
        }

    }, 5000);

} catch (error) {
    console.error('❌ Ошибка при тестировании:', error);
}

console.log('\n📝 Инструкции:');
console.log('1. Скопируйте код в консоль браузера');
console.log('2. Нажмите Enter для выполнения');
console.log('3. Дождитесь завершения тестирования');
console.log('4. Скопируйте результаты и отправьте мне');

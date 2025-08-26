"""
Модуль для заполнения формы отчета
"""

from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger
import time


class FormFiller:
    """Класс для заполнения формы отчета"""

    # Устойчивые локаторы для ReportViewer dropdown
    DROPDOWN_ROOT = (
        By.XPATH,
        "//div[starts-with(@id,'ReportViewerControl_') and contains(@id,'_divDropDown')]"
    )
    
    # NBSP -> пробел и поиск по частям текста
    LABEL_XPATH = (
        ".//label["
        "contains(normalize-space(translate(., '\u00A0',' ')), 'Интернет') and "
        "contains(normalize-space(translate(., '\u00A0',' ')), 'Низкая скорость') and "
        "contains(normalize-space(translate(., '\u00A0',' ')), '3G/4G')"
        "]"
    )

    def __init__(self, driver, logger, iframe_handler, form_elements):
        self.driver = driver
        self.logger = logger
        self.iframe_handler = iframe_handler
        self.form_elements = form_elements

    def set_report_period(self, period_name='произвольный'):
        """Установить период отчета"""
        try:
            self.logger.info(f"📊 Устанавливаем период отчета: {period_name}")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем поле периода отчета с диагностикой
                period_selector = self.form_elements.get_element_selector('period_dropdown')
                period_field = self.iframe_handler.find_element_with_diagnostics(period_selector)

                if not period_field:
                    self.logger.error("❌ Поле периода отчета не найдено")
                    return False

                # Проверяем, что это SELECT элемент
                if period_field.tag_name.lower() != 'select':
                    self.logger.error(f"❌ Поле периода отчета не является SELECT элементом. Найден: {period_field.tag_name}")
                    self.logger.info(f"   ID элемента: {period_field.get_attribute('id')}")
                    self.logger.info(f"   Классы элемента: {period_field.get_attribute('class')}")
                    return False

                # Получаем значение для периода
                period_value = self.form_elements.get_period_value(period_name)
                if not period_value:
                    self.logger.error(f"❌ Неизвестный период: {period_name}")
                    return False

                # Создаем объект Select и выбираем значение
                period_select = Select(period_field)
                period_select.select_by_value(period_value)

                self.logger.info(f"✅ Период отчета установлен: {period_name} (значение: {period_value})")

                # Ждем завершения postback (ASP.NET WebForms)
                self.logger.info("⏳ Ждем завершения postback после выбора периода...")
                time.sleep(3)

                # После postback ищем элементы заново (избегаем stale element reference)
                self.logger.info("🔍 Проверяем готовность элементов после postback...")

                # Проверяем, что поля дат стали доступными
                start_date_selector = self.form_elements.get_element_selector('start_date_field')
                start_date_field = self.iframe_handler.find_element_in_iframe(start_date_selector)

                if start_date_field and not start_date_field.get_attribute('disabled') and 'aspNetDisabled' not in start_date_field.get_attribute('class'):
                    self.logger.info("✅ Поля дат разблокированы после выбора периода")
                else:
                    self.logger.warning("⚠️ Поля дат все еще заблокированы, возможно нужна дополнительная задержка")
                    time.sleep(2)

                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке периода отчета: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def set_start_date(self):
        """Установить дату начала"""
        try:
            self.logger.info("📅 Устанавливаем дату начала")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем поле даты начала
                start_date_selector = self.form_elements.get_element_selector('start_date_field')
                start_date_field = self.iframe_handler.find_element_in_iframe(start_date_selector)

                if not start_date_field:
                    self.logger.error("❌ Поле даты начала не найдено")
                    return False

                # Получаем тестовую дату
                start_date = self.form_elements.get_test_date('start_date')

                # Используем JavaScript для установки значения (поле имеет кастомные обработчики)
                self.logger.info(f"📝 Устанавливаем дату через JavaScript: {start_date}")
                self.driver.execute_script("arguments[0].value = arguments[1];", start_date_field, start_date)

                # Триггерим событие onchange для активации JavaScript обработчиков
                self.logger.info("🔄 Триггерим onchange событие...")
                self.driver.execute_script("arguments[0].onchange();", start_date_field)

                # Ждем завершения postback (ASP.NET WebForms)
                self.logger.info("⏳ Ждем завершения postback...")
                time.sleep(3)

                # После postback ищем элемент заново (избегаем stale element reference)
                self.logger.info("🔍 Ищем элемент даты начала заново после postback...")
                start_date_field = self.iframe_handler.find_element_in_iframe(start_date_selector)
                if not start_date_field:
                    self.logger.error("❌ Элемент даты начала не найден после postback")
                    return False

                # Проверяем, что значение установилось
                actual_value = start_date_field.get_attribute('value')
                if start_date in actual_value:
                    self.logger.info(f"✅ Дата начала установлена: {start_date}")
                else:
                    self.logger.warning(f"⚠️ Дата установлена, но значение отличается: {actual_value}")

                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты начала: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def set_end_date(self):
        """Установить дату окончания"""
        try:
            self.logger.info("📅 Устанавливаем дату окончания")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем поле даты окончания
                end_date_selector = self.form_elements.get_element_selector('end_date_field')
                end_date_field = self.iframe_handler.find_element_in_iframe(end_date_selector)

                if not end_date_field:
                    self.logger.error("❌ Поле даты окончания не найдено")
                    return False

                # Получаем тестовую дату
                end_date = self.form_elements.get_test_date('end_date')

                # Используем JavaScript для установки значения (поле имеет кастомные обработчики)
                self.logger.info(f"📝 Устанавливаем дату через JavaScript: {end_date}")
                self.driver.execute_script("arguments[0].value = arguments[1];", end_date_field, end_date)

                # У поля даты окончания нет onchange обработчика, просто ждем
                self.logger.info("⏳ Ждем применения изменений...")
                time.sleep(2)

                # Проверяем, что значение установилось
                actual_value = end_date_field.get_attribute('value')
                if end_date in actual_value:
                    self.logger.info(f"✅ Дата окончания установлена: {end_date}")
                else:
                    self.logger.warning(f"⚠️ Дата установлена, но значение отличается: {actual_value}")

                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке даты окончания: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def set_reason(self):
        """Установить причину обращения через выпадающий список с чекбоксами"""
        try:
            self.logger.info("🔍 Устанавливаем причину обращения")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # 1. Сначала нажимаем на кнопку выпадающего списка
                dropdown_toggle_selector = self.form_elements.get_dropdown_selector('reason_dropdown_toggle')
                if not dropdown_toggle_selector:
                    self.logger.error("❌ Селектор кнопки выпадающего списка не найден")
                    return False

                dropdown_toggle = self.iframe_handler.find_element_in_iframe(dropdown_toggle_selector)
                if not dropdown_toggle:
                    self.logger.error("❌ Кнопка выпадающего списка не найдена")
                    return False

                self.logger.info("📋 Открываем выпадающий список причины обращения...")
                dropdown_toggle.click()

                # Ждем появления выпадающего списка
                time.sleep(2)

                # 2. Теперь нажимаем "Выделить все" чтобы снять все галочки
                select_all_selector = self.form_elements.get_dropdown_selector('reason_select_all')
                if not select_all_selector:
                    self.logger.error("❌ Селектор 'Выделить все' не найден")
                    return False

                # Пробуем найти чекбокс "Выделить все"
                select_all_checkbox = self.iframe_handler.find_element_in_iframe(select_all_selector)
                if not select_all_checkbox:
                    self.logger.warning("⚠️ Чекбокс 'Выделить все' не найден по селектору, пробуем найти по тексту...")

                    # Fallback: ищем по тексту "Выделить все"
                    try:
                        select_all_checkbox = self.iframe_handler.find_element_in_iframe(
                            ("xpath", "//input[@type='checkbox' and following-sibling::label[contains(text(), 'Выделить все')]]")
                        )
                        if select_all_checkbox:
                            self.logger.info("✅ Чекбокс 'Выделить все' найден по тексту")
                        else:
                            self.logger.warning("⚠️ Чекбокс 'Выделить все' не найден даже по тексту, продолжаем...")
                            # Продолжаем без снятия галочек
                    except:
                        self.logger.warning("⚠️ Не удалось найти 'Выделить все', продолжаем...")
                        # Продолжаем без снятия галочек
                else:
                    self.logger.info("🗑️ Снимаем все галочки через 'Выделить все'...")
                    select_all_checkbox.click()

                                # Ждем применения изменений и исчезновения модального окна
                self.logger.info("⏳ Ждем применения изменений и исчезновения модального окна...")

                # Ждем исчезновения модального окна ожидания
                wait_time = 10
                start_time = time.time()
                while time.time() - start_time < wait_time:
                    try:
                        # Ищем модальное окно ожидания
                        modal = self.driver.find_element("xpath",
                            "//div[contains(@class, 'wait-indicator-dialog') and contains(@class, 'in')]")
                        if modal.is_displayed():
                            self.logger.info("⏳ Модальное окно ожидания активно, ждем...")
                            time.sleep(0.5)
                            continue
                        else:
                            self.logger.info("✅ Модальное окно ожидания исчезло")
                            break
                    except:
                        # Модальное окно не найдено - значит исчезло
                        self.logger.info("✅ Модальное окно ожидания не найдено")
                        break

                                # Дополнительная задержка для стабилизации
                time.sleep(2)
                self.logger.info("✅ Готовы к выбору чекбокса")

                # 3. ⚠️ ВАЖНЫЙ ПЕРЕХОД из iframe в корень, дальше ищем не в iframe
                self.logger.info("🔄 Переходим в корень страницы для поиска label в dropdown...")
                
                # Если после "Выделить все" dropdown закрылся — переоткроем
                select_ok = self.select_reason_label("#ReportViewerControl_ctl04_ctl23_divDropDown_ctl00")
                if not select_ok:
                    self.logger.error("❌ Label 'Интернет >> Низкая скорость в 3G/4G' не найден внутри dropdown")
                    return False
                
                self.logger.info("✅ Причина обращения установлена: Низкая скорость в 3G/4G")
                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при установке причины обращения: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

    def _find_label_in_all_iframes(self, label_xpath):
        """Найти label во всех доступных iframe'ах"""
        try:
            self.logger.info("🔍 Поиск label во всех iframe'ах...")

                        # Возвращаемся в основной документ для поиска всех iframe'ов
            self.iframe_handler.switch_to_main_document()

            # СНАЧАЛА ищем в main document (панель могла уехать наверх)
            self.logger.info("🔍 Сначала ищем в main document...")
            try:
                label = self.driver.find_element("xpath", label_xpath)
                if label and label.is_displayed():
                    label_text = label.text.strip()
                    self.logger.info(f"✅ Label найден в main document: '{label_text}'")

                    # Проверяем что это нужный label
                    if ("Интернет" in label_text or "Интернет" in label.get_attribute("innerHTML", "")) and \
                       ("Низкая скорость" in label_text or "Низкая скорость" in label.get_attribute("innerHTML", "")) and \
                       ("3G/4G" in label_text or "3G/4G" in label.get_attribute("innerHTML", "")):
                        self.logger.info(f"🎯 Найден правильный label в main document!")
                        return label
                    else:
                        self.logger.info(f"⚠️ Label в main document не подходит: '{label_text}'")
            except:
                self.logger.info("🔍 Label не найден в main document")

            # Теперь ищем все iframe'ы на странице
            iframes = self.driver.find_elements("tag name", "iframe")
            self.logger.info(f"📋 Найдено {len(iframes)} iframe'ов на странице")

            for i, iframe in enumerate(iframes):
                try:
                    self.logger.info(f"🔍 Проверяем iframe {i+1}/{len(iframes)}...")

                    # Переключаемся на iframe
                    self.driver.switch_to.frame(iframe)

                    # Ищем label в текущем iframe
                    try:
                        label = self.driver.find_element("xpath", label_xpath)
                        if label and label.is_displayed():
                            label_text = label.text.strip()
                            self.logger.info(f"✅ Label найден в iframe {i+1}: '{label_text}'")

                            # Проверяем что это нужный label (более гибкая проверка)
                            if ("Интернет" in label_text or "Интернет" in label.get_attribute("innerHTML", "")) and \
                               ("Низкая скорость" in label_text or "Низкая скорость" in label.get_attribute("innerHTML", "")) and \
                               ("3G/4G" in label_text or "3G/4G" in label.get_attribute("innerHTML", "")):
                                self.logger.info(f"🎯 Найден правильный label в iframe {i+1}!")
                                return label
                            else:
                                self.logger.info(f"⚠️ Label в iframe {i+1} не подходит: '{label_text}'")
                                # Дополнительная диагностика
                                try:
                                    inner_html = label.get_attribute("innerHTML", "")
                                    self.logger.info(f"🔍 innerHTML: '{inner_html}'")
                                except:
                                    pass
                    except:
                        # Label не найден в этом iframe
                        pass

                    # Возвращаемся в основной документ для следующего iframe
                    self.driver.switch_to.default_content()

                except Exception as e:
                    self.logger.warning(f"⚠️ Ошибка при проверке iframe {i+1}: {e}")
                    # Возвращаемся в основной документ
                    try:
                        self.driver.switch_to.default_content()
                    except:
                        pass
                    continue

            self.logger.warning("⚠️ Label не найден ни в одном iframe")
            return None

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске во всех iframe'ах: {e}")
            # Возвращаемся в основной документ
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return None

    def _find_label_on_page(self, label_xpath):
        """Найти label на всей странице (не только в iframe'ах)"""
        try:
            self.logger.info("🔍 Поиск label на всей странице...")

            # Возвращаемся в основной документ
            self.iframe_handler.switch_to_main_document()

            # Ищем label на основной странице
            try:
                labels = self.driver.find_elements("xpath", label_xpath)
                self.logger.info(f"📋 Найдено {len(labels)} label'ов на основной странице")

                for i, label in enumerate(labels):
                    try:
                        if label.is_displayed():
                            label_text = label.text.strip()
                            self.logger.info(f"✅ Label {i+1} на основной странице: '{label_text}'")

                            # Проверяем что это нужный label
                            if ("Интернет" in label_text or "Интернет" in label.get_attribute("innerHTML", "")) and \
                               ("Низкая скорость" in label_text or "Низкая скорость" in label.get_attribute("innerHTML", "")) and \
                               ("3G/4G" in label_text or "3G/4G" in label.get_attribute("innerHTML", "")):
                                self.logger.info(f"🎯 Найден правильный label на основной странице!")
                                return label
                            else:
                                self.logger.info(f"⚠️ Label {i+1} не подходит: '{label_text}'")
                                # Дополнительная диагностика
                                try:
                                    inner_html = label.get_attribute("innerHTML", "")
                                    self.logger.info(f"🔍 innerHTML: '{inner_html}'")
                                except:
                                    pass
                    except Exception as e:
                        self.logger.warning(f"⚠️ Ошибка при проверке label {i+1}: {e}")
                        continue

            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка при поиске label'ов на странице: {e}")

            # Если не найден, пробуем искать по более простому селектору
            self.logger.info("🔍 Пробуем простой поиск по тексту...")
            try:
                all_labels = self.driver.find_elements("tag name", "label")
                self.logger.info(f"📋 Всего label'ов на странице: {len(all_labels)}")

                for i, label in enumerate(all_labels):
                    try:
                        if label.is_displayed():
                            label_text = label.text.strip()
                            if label_text and len(label_text) > 10:  # Только непустые и длинные
                                self.logger.info(f"📝 Label {i+1}: '{label_text}'")

                                # Проверяем на нужный текст
                                if "Интернет" in label_text and "Низкая скорость" in label_text and "3G/4G" in label_text:
                                    self.logger.info(f"🎯 Найден нужный label по простому поиску!")
                                    return label
                    except:
                        continue

            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка при простом поиске: {e}")

            self.logger.warning("⚠️ Label не найден ни на основной странице, ни по простому поиску")
            return None

        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске на странице: {e}")
            return None

    def _open_dropdown_again_if_closed(self, toggle_in_iframe_locator, timeout=10):
        """Если корневого dropdown нет/невидим — снова кликаем toggle внутри iframe"""
        try:
            root = self.driver.find_element(*self.DROPDOWN_ROOT)
            if not root.is_displayed():
                self.logger.info("🔄 Dropdown невидим, переоткрываем...")
                # Возвращаемся в iframe для клика
                self.iframe_handler.switch_to_iframe()
                toggle = self.iframe_handler.find_element_in_iframe(toggle_in_iframe_locator)
                toggle.click()
                # Возвращаемся в корень
                self.driver.switch_to.default_content()
        except:
            self.logger.info("🔄 Dropdown не найден, открываем...")
            # Возвращаемся в iframe для клика
            self.iframe_handler.switch_to_iframe()
            toggle = self.iframe_handler.find_element_in_iframe(toggle_in_iframe_locator)
            toggle.click()
            # Возвращаемся в корень
            self.driver.switch_to.default_content()
        
        # Ждем появления dropdown
        wait = WebDriverWait(self.driver, timeout)
        root = wait.until(EC.visibility_of_element_located(self.DROPDOWN_ROOT))
        self.logger.info("✅ Dropdown открыт и видим")

    def _find_label_in_dropdown(self, timeout=10):
        """Найти label внутри контейнера dropdown"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            root = wait.until(EC.visibility_of_element_located(self.DROPDOWN_ROOT))
            
            # У dropdown внутри есть прокручиваемая область <div style="overflow:auto">
            try:
                scrollbox = root.find_element(By.XPATH, ".//div[descendant::table and contains(@style,'overflow')]")
                self.logger.info("✅ Найдена прокручиваемая область dropdown")
            except:
                scrollbox = root
                self.logger.info("⚠️ Прокручиваемая область не найдена, используем весь dropdown")
            
            # Пробуем найти сразу:
            try:
                label = scrollbox.find_element(By.XPATH, self.LABEL_XPATH)
                self.logger.info("✅ Label найден сразу")
                return label
            except:
                self.logger.info("🔍 Label не найден сразу, выполняем пошаговый скролл...")
                
                # Если не видно, скроллим и ищем по шагам
                total = self.driver.execute_script("return arguments[0].scrollHeight", scrollbox)
                view = self.driver.execute_script("return arguments[0].clientHeight", scrollbox)
                step = max(view // 2, 80)
                
                self.logger.info(f"📜 Высота: {total}, видимая: {view}, шаг: {step}")
                
                for y in range(0, total + step, step):
                    self.driver.execute_script("arguments[0].scrollTop = arguments[1];", scrollbox, y)
                    try:
                        el = scrollbox.find_element(By.XPATH, self.LABEL_XPATH)
                        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                        self.logger.info(f"✅ Label найден при скролле на позиции {y}")
                        return el
                    except:
                        continue
                
                self.logger.warning("⚠️ Label не найден даже после пошагового скролла")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при поиске label в dropdown: {e}")
            return None

    def select_reason_label(self, toggle_in_iframe_locator):
        """Выбрать label причины обращения"""
        try:
            # 1) После «выделить все» дождаться тишины (логика invisibility — ок)
            # 2) Критично: вернуться в корень и убедиться, что dropdown открыт
            self.driver.switch_to.default_content()
            self._open_dropdown_again_if_closed(toggle_in_iframe_locator)

            # 3) Найти label внутри КОНТЕЙНЕРА dropdown
            label = self._find_label_in_dropdown()
            if not label:
                return False

            # 4) Клик по label (надёжнее, чем по input)
            try:
                wait = WebDriverWait(self.driver, 5)
                wait.until(EC.element_to_be_clickable(label)).click()
                self.logger.info("✅ Label успешно выбран")
            except:
                self.driver.execute_script("arguments[0].click();", label)
                self.logger.info("✅ Label выбран через JavaScript")

            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при выборе label: {e}")
            return False

    def submit_report(self):
        """Отправить отчет"""
        try:
            self.logger.info("🚀 Отправляем отчет")

            # Переключаемся на iframe
            if not self.iframe_handler.switch_to_iframe():
                return False

            try:
                # Ищем кнопку отправки
                submit_selector = self.form_elements.get_element_selector('submit_button')
                submit_button = self.iframe_handler.wait_for_element_clickable(submit_selector)

                if not submit_button:
                    self.logger.error("❌ Кнопка отправки не найдена или не кликабельна")
                    return False

                # Нажимаем кнопку
                submit_button.click()

                self.logger.info("✅ Отчет отправлен")
                return True

            finally:
                # Возвращаемся в основной документ
                self.iframe_handler.switch_to_main_document()

        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке отчета: {e}")
            # Возвращаемся в основной документ в случае ошибки
            try:
                self.iframe_handler.switch_to_main_document()
            except:
                pass
            return False

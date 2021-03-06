# bgbilling-web-cloud
Альтернативный личный кабинет для универсальной биллинговой системы BGBilling. Проект реализован на свободном фреймворке django и представляет набор из нескольких логически независимых модулей:

* core - ядро xml/json запросов к сервису
* access - регистрация / аторизация / аутентификация пользователей, восстановление доступа
* bill - детализация расходов / формирования счетов на оплату / пополнение счета через онлайн сервисы (yandex касса)
* collocation - учет размещаемого оборудования (для ДЦ)
* home - основные параметры договора / быстрый переход между подключенными услугами и модулями
* inet - просмотр и управление параметрами сети, ip адреса, vlan'ы, скорость подключения.
* virt - управление виртуальными серверами. Данный модуль основан на открытом проекте WebVirtCloud https://github.com/retspen/webvirtcloud
* support - система заявок и обращений в техподдержку. Данный модуль основан на открытом проекте osTicket
Для управления параметрами договора, приложение использует стандартное API сервиса BGBilling в виде xml и json запросов.

v 2.0
* Реализована регистрация юридических и физических лиц
* Автозаполнение полей при регистрации с сервиса DaData
* Реализовано автоматическое формирование договоров для юридических и физических лиц
* Реализовано автоматическое формирование счетов на оплату
* Возможность производить оплату через онлайн сервисы
* Возможность создания обращения и заявок в техподдержку из личного кабинета
* Управление арендованными виртуальными машинами

#include <QtTest/QtTest>
{{TEST_INCLUDES}}

class {{TEST_CLASS_NAME}} : public QObject
{
    Q_OBJECT

private slots:
    {{TEST_METHODS}}
};

QTEST_MAIN({{TEST_CLASS_NAME}})
#include "{{TEST_CLASS_NAME}}.moc"

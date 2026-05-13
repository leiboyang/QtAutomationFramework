#include <QApplication>
{{MAIN_INCLUDES}}

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    {{MAIN_BODY}}
    return app.exec();
}

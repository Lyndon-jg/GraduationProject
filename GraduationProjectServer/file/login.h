#ifndef LOGIN_H
#define LOGIN_H

#include <QDialog>
#include <QUdpSocket>
#include<sqlite3.h>
#include<QTimer>

namespace Ui {
class login;
}

class login : public QDialog
{
    Q_OBJECT

public:
    explicit login(QWidget *parent = 0);
    ~login();
private slots:

    void read_slot();//yong

    void on_jizhu_mima_radioButton_clicked(bool checked);

    void on_name_lineEdit_textChanged(const QString &arg1);

    void on_zhuce_pushButton_clicked();//yong

    void on_zhaohui_pushButton_clicked();

    void on_denglu_pushButton_clicked();//yong

private:
    Ui::login *ui;
    QUdpSocket *socket;
    bool isclicked;
    sqlite3 *db;
    QTimer *time;
    int rmaddr();
};

#endif // LOGIN_H

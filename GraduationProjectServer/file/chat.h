#ifndef CHAT_H
#define CHAT_H

#include <QDialog>
#include<QTimer>
#include<QUdpSocket>
#include<QTreeWidgetItem>

namespace Ui {
class chat;
}

class chat : public QDialog
{
    Q_OBJECT
private slots:

    void timeout_slot();//yong

    void on_treeWidget_doubleClicked(const QModelIndex &index);//yong

    void read_slot();//yong

    void on_fasong_pushButton_clicked();//yong

    void on_add_pushButton_clicked();

    void on_pushButton_clicked();

    void on_zhuxiao_pushButton_clicked();

public:
    explicit chat(QWidget *parent = 0);
    ~chat();
    void showchat(QString str);

private:
    Ui::chat *ui;
    QTimer *time;
    QString curcount;
    QUdpSocket *socket;
};

#endif // CHAT_H

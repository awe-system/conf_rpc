#ifndef FUNC_FORM_H
#define FUNC_FORM_H

#include <QWidget>
#include <qmainwindow.h>

class func_form;
class func_form_cb
{
public:
    virtual void complete(func_form * from) = 0;
};


namespace Ui {
class func_form;
}

class func_form : public Qdailog
{
    Q_OBJECT

public:
    explicit func_form(QWidget *parent = nullptr);
    ~func_form();
public:
    func_form_cb * farther;
    QString get_res();

private slots:
    void on_func_form_destroyed();

    void on_func_form_destroyed(QObject *arg1);

private:
    Ui::func_form *ui;
};

#endif // FUNC_FORM_H

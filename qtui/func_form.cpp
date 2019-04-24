#include "func_form.h"
#include "ui_func_form.h"


func_form::func_form(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::func_form)
{
    ui->setupUi(this);
}

func_form::~func_form()
{
    delete ui;
}

QString func_form::get_res()
{
    return "ssss";
}

void func_form::on_func_form_destroyed()
{
     farther->complete(this);
}

void func_form::on_func_form_destroyed(QObject *arg1)
{
     farther->complete(this);
}

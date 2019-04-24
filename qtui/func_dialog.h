#ifndef FUNC_DIALOG_H
#define FUNC_DIALOG_H

#include <QDialog>

#include <lt_data/json_obj.h>

namespace Ui {
class Dialog;
}

class Dialog;


#define FUNC_NAME   "func_name"
#define FUNC_TYPE   "func_type"
#define FUNC_PARAMS "func_params"
#define PARAM_TYPE  "param_type"
#define PARAM_INOUT "param_inout"
#define PARAM_NAME  "param_name"

class Dialog : public QDialog
{
    Q_OBJECT
public:
    bool is_canceled = true;
    explicit Dialog(QWidget *parent = nullptr);
    ~Dialog();

    json_obj to_json();

    void from_json(const json_obj& obj);

private:
    void add_empty_param_at(int row);
    void alert(const QString &str);
    void swap(int i,int  j);

    bool is_param_ok();

private slots:
    void on_Dialog_destroyed();

    void on_add_bt_clicked();

    void on_del_bt_clicked();

    void on_moveup_clicked();

    void on_pushButton_2_clicked();

    void on_pushButton_3_clicked();

    void on_movedown_clicked();

private:
    Ui::Dialog *ui;
};

#endif // FUNC_DIALOG_H

#include "func_dialog.h"
#include "ui_dialog.h"

#include <QMessageBox>

Dialog::Dialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::Dialog)
{
    ui->setupUi(this);
    ui->comboBox_type->addItem("sync");
    ui->comboBox_type->addItem("async");
    ui->comboBox_type->addItem("clientsync");
}

Dialog::~Dialog()
{
    delete ui;
}


void Dialog::from_json(const json_obj &obj)
{
    int row = 0;
    ui->funcname->setText(QString::fromStdString(obj[FUNC_NAME].s_val));
    ui->comboBox_type->setCurrentText(QString::fromStdString(obj[FUNC_TYPE].s_val));
    for ( auto param : obj[FUNC_PARAMS].array_val)
    {
        add_empty_param_at(row);
        auto type_box = (QComboBox *)ui->tableWidget->cellWidget(row, 1);
        auto inout_box = (QComboBox *)ui->tableWidget->cellWidget(row, 2);
        ui->tableWidget->item(row,0)->setText(QString::fromStdString(param[PARAM_NAME].s_val));
        type_box->setCurrentText(QString::fromStdString(param[PARAM_TYPE].s_val));
        inout_box->setCurrentText(QString::fromStdString(param[PARAM_INOUT].s_val));
        ++row;
    }
}

json_obj Dialog::to_json()
{
    json_obj obj(FUNC_NAME, ui->funcname->text().toStdString());

    obj[FUNC_TYPE] = ui->comboBox_type->currentText().toStdString();
    json_obj params;
    for(int row = 0; row < ui->tableWidget->rowCount() ;++row)
    {
        auto type_box = (QComboBox *)ui->tableWidget->cellWidget(row, 1);
        auto inout_box = (QComboBox *)ui->tableWidget->cellWidget(row, 2);
        auto val_name = ui->tableWidget->item(row,0)->text();
        json_obj item(PARAM_NAME, val_name.toStdString());
        item[PARAM_TYPE] = type_box->currentText().toStdString();
        item[PARAM_INOUT] = inout_box->currentText().toStdString();
        params.append(item);
    }
    obj[FUNC_PARAMS] = params;
    return obj;
}

void Dialog::add_empty_param_at(int row)
{
    ui->tableWidget->insertRow(row);
    QComboBox *box = new QComboBox(this);
    box->addItem("string");
    box->addItem("char_p");
    box->addItem("ulong");
    box->addItem("uint");
    box->addItem("bool");
    box->addItem("void_p");
    box->addItem("data");
    QComboBox *inoutbox = new QComboBox(this);
    inoutbox->addItem("in");
    inoutbox->addItem("out");
    inoutbox->addItem("inout");

    ui->tableWidget->setItem(row,0, new QTableWidgetItem(""));
    ui->tableWidget->setCellWidget(row,1,box);
    ui->tableWidget->setCellWidget(row,2,inoutbox);
}


void Dialog::alert(const QString &str)
{
    QMessageBox *msg = new QMessageBox("Alert",str,
                                       QMessageBox::Critical,QMessageBox::Ok | QMessageBox::Default,
                                       QMessageBox::Cancel | QMessageBox::Escape,0);
    msg->show();
}

void Dialog::swap(int i, int j)
{
    QString tmp_str_1 = "", tmp_str_2 = "";
    QComboBox * type_box_1, *type_box_2;
    QComboBox * inout_box_1, * inout_box_2;
    QString tmp_str;

    tmp_str_1 = ui->tableWidget->item(i, 0)->text();
    tmp_str_2 = ui->tableWidget->item(j, 0)->text();

    type_box_1 = (QComboBox *)ui->tableWidget->cellWidget(i, 1);
    type_box_2 = (QComboBox *)ui->tableWidget->cellWidget(j, 1);

    inout_box_1 = (QComboBox *)ui->tableWidget->cellWidget(i, 2);
    inout_box_2 = (QComboBox *)ui->tableWidget->cellWidget(j, 2);

    ui->tableWidget->item(i, 0)->setText( tmp_str_2);
    ui->tableWidget->item(j, 0)->setText(tmp_str_1);

    tmp_str = type_box_1->currentText();
    type_box_1->setCurrentText(type_box_2->currentText());
    type_box_2->setCurrentText(tmp_str);

    tmp_str = type_box_1->currentText();
    inout_box_1->setCurrentText(inout_box_2->currentText());
    inout_box_2->setCurrentText(tmp_str);
}

bool Dialog::is_param_ok()
{
    for(int row = 0 ;row < ui->tableWidget->rowCount(); ++row)
    {
        if(ui->tableWidget->item(row,0)->text() == "")
            return false;
    }
    return true;
}

void Dialog::on_Dialog_destroyed()
{
}

void Dialog::on_add_bt_clicked()
{
    int row = ui->tableWidget->currentRow();
    if(row == -1)
    {
        row = 0;
    }

    add_empty_param_at(row);
}

void Dialog::on_del_bt_clicked()
{
    int row = ui->tableWidget->currentRow();
    if(row == -1)
    {
        return;
    }
    ui->tableWidget->removeRow(row);

}

void Dialog::on_moveup_clicked()
{
    int row = ui->tableWidget->currentRow();
    if(row > 0)
    {
        swap(row, row-1);
        return;
    }
}

void Dialog::on_pushButton_2_clicked()
{
    if(ui->funcname->text() == "")
    {
        alert("fucnname字段不能为空");
        return;
    }

    if( !is_param_ok() )
    {
        alert("paramname字段不能为空");
        return;
    }
    is_canceled = false;
    close();
}

void Dialog::on_pushButton_3_clicked()
{
     close();
}

void Dialog::on_movedown_clicked()
{
    int row = ui->tableWidget->currentRow();
    if(row >= 0 && row + 1 <  ui->tableWidget->rowCount())
    {
        swap(row, row+1);
        return;
    }
}

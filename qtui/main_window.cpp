#include "main_window.h"
#include "ui_main_window.h"
#include "func_dialog.h"

#include <QDomDocument>
#include <QFileDialog>
#include <QMessageBox>
#include <QSizePolicy>
#include <QTextEdit>
#include <QTextStream>
#include <QXmlStreamWriter>
#include <lt_function/utils.h>


main_window::main_window(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::main_window)
{
    ui->setupUi(this);
    ui->comboBox_cli->addItem("C++");
    ui->comboBox_cli->addItem("python");
    ui->comboBox_cli->addItem("python/C++");
    ui->comboBox_serv->addItem("C++");
    ui->func_list->resizeColumnsToContents();
    ui->func_list->horizontalHeader();
}

void main_window::alert(const QString &str)
{
    QMessageBox *msg = new QMessageBox("Alert",str,
                                       QMessageBox::Critical,QMessageBox::Ok | QMessageBox::Default,
                                       QMessageBox::Cancel | QMessageBox::Escape,0);
    msg->show();
}

main_window::~main_window()
{
    delete ui;
}

void main_window::add_key_to_map(const QString &func_key,  const json_obj & obj)
{
    if(funcs.end() != funcs.find(func_key.toStdString()))
    {
        alert("same func name exsit");
        return;
    }
    funcs[func_key.toStdString()] = obj;
    funcs_by_num.push_back(obj);
}

void main_window::reove_from_map(const QString &func_key)
{
    funcs.erase(func_key.toStdString());
}

void main_window::reove_from_list(int row)
{
    funcs_by_num.erase(funcs_by_num.begin()+ row);
}


bool main_window::is_xml_empty()
{
    if (ui->xml_path->text() == "")
    {
        return true;
    }
    return false;
}

void main_window::recovery_port(QDomNode *node)
{
    QDomElement e=node->toElement();
    QString port_str = e.attribute("content");
    ui->port_box->setValue(port_str.toInt());
}

void main_window::recovery_project(QDomNode *node)
{
    QDomElement e=node->toElement();
    QString project_str = e.attribute("content");
    ui->project->setText(project_str);
}

void main_window::recovery_client(QDomNode *node)
{
    QDomElement e=node->toElement();
    QString type = e.attribute("type");
    ui->comboBox_cli->setCurrentText(type);

    QString withping_str = e.attribute("withping");

    if(withping_str == "true") ui->withping->setCheckState(Qt::Checked);
    else ui->withping->setCheckState(Qt::Unchecked);

    QString nmspace = e.attribute("namespace");
    ui->cli_namespace->setText(nmspace);

    QString filename = e.attribute("filename");
    ui->cli_file->setText(filename);

    try {
        QString classname = e.attribute("classname");
        ui->cli_classname->setText(classname);
    } catch (...) {

    }
}

void main_window::recovery_server(QDomNode *node)
{
    QDomElement e=node->toElement();
    QString type = e.attribute("type");
    ui->comboBox_serv->setCurrentText(type);

    QString nmspace = e.attribute("namespace");
    ui->serv_namespace->setText(nmspace);

    QString filename = e.attribute("filename");
    ui->serv_file->setText(filename);

    try {
        QString classname = e.attribute("classname");
        ui->serv_classname->setText(classname);
    } catch (...) {

    }
}

static void recovey_func_name(QDomElement *e, json_obj & obj)
{
    QString func_name = e->attribute("name");
    obj[FUNC_NAME] = func_name.toStdString();
}

static void recovey_func_type(QDomElement *e, json_obj & obj)
{
    QString func_type = e->attribute("type");
    obj[FUNC_TYPE] = func_type.toStdString();
    if(obj[FUNC_TYPE] == "async")
    {
        try {
            QString sub_type = e->attribute("subtype");
            if(sub_type == "sync")
            {
                obj[FUNC_TYPE] = "clientsync";
            }
        } catch (...) {

        }
    }
}

static void recovey_param(QDomNode *n, json_obj & obj)
{
    QDomElement e=n->toElement();
    QString name = e.attribute("name");
    obj[PARAM_NAME] = name.toStdString();

    QString value = e.attribute("value");
    obj[PARAM_TYPE] = value.toStdString();

    QString inout = e.attribute("type");
    obj[PARAM_INOUT] = inout.toStdString();
}

static void recovey_func_params(QDomElement *e, json_obj & obj)
{
    try {
        cout<<"recovey_func_params"<<endl;
        QDomNodeList params= e->childNodes();
        obj[FUNC_PARAMS] = json_obj();
        for(int i=0;i<params.count();i++) //遍历子元素，count和size都可以用,可用于标签数计数
        {
            QDomNode n = params.at(i);
            if(n.isElement() && n.nodeName() == "param")
            {
                json_obj tmp_obj;
                recovey_param(&n, tmp_obj);
                obj[FUNC_PARAMS].append(tmp_obj);
            }
        }
        cout<<"recovey_func_params normal out"<<endl;
    } catch (...) {

        cout<<"recovey_func_params except"<<endl;
    }
}

void main_window::recovery_func(QDomNode *node)
{
    QDomElement e=node->toElement();
    json_obj obj;
    recovey_func_name(&e, obj);
    recovey_func_type(&e, obj);
    recovey_func_params(&e, obj);
    cout<<obj.dumps()<<endl;
    add_json_to_func(obj);
}

#define check_err_out(is_err,msg) \
do\
{\
    if(is_err)\
    {\
        alert(msg);\
        throw 1;\
    }\
}\
while(0)

void main_window::recovery_node(QDomNode *node)
{
    if(node->nodeName() == "port")
    {
        recovery_port(node);
    }
    else if(node->nodeName() == "project")
    {
        recovery_project(node);
    }
    else if(node->nodeName() == "client")
    {
        recovery_client(node);
    }
    else if(node->nodeName() == "server")
    {
        recovery_server(node);
    }
    else if(node->nodeName() == "func")
    {
        recovery_func(node);
    }
}

void main_window::recovery(QDomDocument *doc)
{
    QDomElement root=doc->documentElement();
    check_err_out(root.nodeName() != "funcs", "xml need funcs");
    QDomNode node=root.firstChild();
    while(!node.isNull())
    {
        if(node.isElement())
        {
            recovery_node(&node);
        }
        node=node.nextSibling();
    }
}

void main_window::load_file(const QString &path)
{
    try {
        QFile file(path);
        if(!file.open(QFile::ReadOnly)) throw 1;
        QDomDocument doc;
        if(!doc.setContent(&file))
        {
            file.close();
            throw  2;
        }
        file.close();
        recovery(&doc);
    } catch (...) {
        alert("加载失败");
    }
}

void main_window::save_file(const QString &path)
{
    try {
          QFile file(path);
        if(!file.open(QFile::WriteOnly|QFile::Truncate))
                return;
        QXmlStreamWriter writer(&file);

        save(&writer);

        file.close();
    } catch (...) {
        alert("加载失败");
    }
}

void main_window::save_port(QXmlStreamWriter *writer)
{
     writer->writeStartElement("port");
     writer->writeAttribute("content", ui->port_box->text());
     writer->writeEndElement();
}

void main_window::save_project(QXmlStreamWriter *writer)
{
    writer->writeStartElement("project");
    writer->writeAttribute("content", ui->project->text());
    writer->writeEndElement();
}

void main_window::save_client(QXmlStreamWriter *writer)
{
    writer->writeStartElement("client");
    writer->writeAttribute("type", ui->comboBox_cli->currentText());
    writer->writeAttribute("namespace", ui->cli_namespace->text());
    writer->writeAttribute("filename", ui->cli_file->text());
    if(ui->withping->isChecked()) writer->writeAttribute("withping", "true");
    if(ui->cli_classname->text() != "") writer->writeAttribute("classname", ui->cli_classname->text());
    writer->writeEndElement();
}

void main_window::save_server(QXmlStreamWriter *writer)
{
    writer->writeStartElement("server");
    writer->writeAttribute("type", ui->comboBox_serv->currentText());
    writer->writeAttribute("namespace", ui->serv_namespace->text());
    writer->writeAttribute("filename", ui->serv_file->text());
    if(ui->serv_classname->text() != "") writer->writeAttribute("classname", ui->serv_classname->text());
    writer->writeEndElement();
}

void main_window::save_params(QXmlStreamWriter *writer, const json_obj &obj)
{
    for(auto param : obj[FUNC_PARAMS].array_val)
    {
        writer->writeStartElement("param");
        writer->writeAttribute("name", param[PARAM_NAME].s_val.c_str());
        writer->writeAttribute("value", param[PARAM_TYPE].s_val.c_str());
        writer->writeAttribute("type", param[PARAM_INOUT].s_val.c_str());
        writer->writeEndElement();
    }
}

static QString functype_by_obj(const json_obj & obj)
{
    if(obj[FUNC_TYPE].s_val == "sync") return "sync";
    if(obj[FUNC_TYPE].s_val == "async") return "async";
    if(obj[FUNC_TYPE].s_val == "clientsync") return "async";
}

static QString subtype_by_obj(const json_obj & obj)
{
    if(obj[FUNC_TYPE].s_val == "clientsync") return "sync";
    return "";
}

void main_window::save_func(QXmlStreamWriter *writer)
{
    for(auto it : funcs_by_num)
    {
        writer->writeStartElement("func");
        writer->writeAttribute("name", it[FUNC_NAME].s_val.c_str());
        writer->writeAttribute("type", functype_by_obj(it));
        if(subtype_by_obj(it) != "") writer->writeAttribute("subtype", subtype_by_obj(it));
        save_params(writer, it);
        writer->writeEndElement();
    }
}

void main_window::save(QXmlStreamWriter *writer)
{
    writer->setAutoFormatting(true);
    writer->writeStartDocument("1.0", true);
    writer->writeStartElement("funcs");
    save_port(writer);
    save_project(writer);
    save_client(writer);
    save_server(writer);
    save_func(writer);
    writer->writeEndElement();
    writer->writeEndDocument();
}

void main_window::on_add_func_clicked()
{
    Dialog *dlg = new Dialog;
    this->setHidden(true);
    dlg->setModal(true);

    dlg->exec();
    this->setHidden(false);

    add_res_to_func_list(dlg);

    delete dlg;
}


void main_window::edit_item(QListWidgetItem *item)
{
    int row = ui->func_list->currentRow();
    if(row<0) return;
    Dialog *dlg = new Dialog;
    this->setHidden(true);
    dlg->setModal(true);
    QTextEdit * edit = (QTextEdit *)ui->func_list->cellWidget(row, 0);
    dlg->from_json(funcs[edit->toPlainText().toStdString()]);
    dlg->exec();
    this->setHidden(false);
    update_res_to_func_list(row, dlg);
    delete dlg;
}

static QString get_item_string(const json_obj & obj)
{
    QString res = QString(obj[FUNC_TYPE].s_val.c_str()) + QString(" int ")
            +  QString(obj[FUNC_NAME].s_val.c_str()) + QString("(");

    for(int row = 0; row < obj[FUNC_PARAMS].array_val.size() ;++row)
    {
        res += obj[FUNC_PARAMS][row][PARAM_INOUT].s_val.c_str();
        res += " ";
        res += obj[FUNC_PARAMS][row][PARAM_TYPE].s_val.c_str();
        res += " ";
        res += obj[FUNC_PARAMS][row][PARAM_NAME].s_val.c_str();;
        if(row != obj[FUNC_PARAMS].array_val.size() -1 )
        {
            res += " , ";
        }
    }
    res += QString(");");
    return res;
}

void main_window::add_json_to_func(const json_obj &obj)
{
    QString str = get_item_string(obj);
    add_string_to_func_list(str);
    add_key_to_map(str,obj);
}

void main_window::update_funclist_format()
{
    for(int i = 0; i < ui->func_list->rowCount(); i++)
    {
        QTextEdit * edit = (QTextEdit *)ui->func_list->cellWidget(i, 0);
        edit->setReadOnly(true);
        edit->setFixedSize(edit->toPlainText().count()*13 + 5,edit->height());
        edit->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);
        update_color(edit);
    }
    ui->func_list->resizeColumnsToContents();
//    ui->func_list->resizeRowsToContents();
    ui->func_list->horizontalHeader();
}

void main_window::update_color(QTextEdit *item)
{
    update_color_key_color(item, QString("async"),Qt::green);
    update_color_key_color(item, QString("sync"),Qt::green);
    update_color_key_color(item, QString("clientsync"),Qt::green);

    update_color_key_color(item, QString("in"),Qt::gray);
    update_color_key_color(item, QString("out"),Qt::gray);
    update_color_key_color(item, QString("inout"),Qt::gray);

    update_color_key_color(item, QString("string"),Qt::blue);
    update_color_key_color(item, QString("char_p"),Qt::blue);
    update_color_key_color(item, QString("ulong"),Qt::blue);
    update_color_key_color(item, QString("int"),Qt::blue);
    update_color_key_color(item, QString("uint"),Qt::blue);
    update_color_key_color(item, QString("bool"),Qt::blue);
    update_color_key_color(item, QString("void_p"),Qt::blue);
    update_color_key_color(item, QString("data"),Qt::blue);
}

void main_window::update_color_key_color(QTextEdit *item, const QString &key, const QBrush &brush)
{
    QString searchString = key;
    QTextDocument *document = item->document();

    if (searchString.isEmpty()) {
        return;
    }
    QTextCursor highlightCursor(document);
    QTextCursor cursor(document);

    cursor.beginEditBlock();

    QTextCharFormat plainFormat(highlightCursor.charFormat());
    QTextCharFormat colorFormat = plainFormat;
    colorFormat.setForeground(brush);

    while (!highlightCursor.isNull() && !highlightCursor.atEnd()) {
        highlightCursor = document->find(searchString, highlightCursor,
                                         QTextDocument::FindWholeWords);

        if (!highlightCursor.isNull()) {
            highlightCursor.movePosition(QTextCursor::WordRight,
                                         QTextCursor::KeepAnchor);
            highlightCursor.mergeCharFormat(colorFormat);
        }
    }
    cursor.endEditBlock();
}


void main_window::add_string_to_func_list(QString &str)
{
    int cur = ui->func_list->rowCount();
    if(cur == -1)
    {
        cur = 0;
    }
    ui->func_list->insertRow(cur);
    QTextEdit *item = new QTextEdit(str);
    ui->func_list->setCellWidget(cur,0, item);

    update_funclist_format();
}

void main_window::clear()
{
    while(ui->func_list->rowCount()> 0)
    {
        ui->func_list->selectRow(0);
        remove_from_listview(0);
    }
}

void main_window::add_res_to_func_list(Dialog *dlg)
{
    if(!dlg->is_canceled)
    {
        json_obj obj = dlg->to_json();
        add_json_to_func(obj);
    }
}

void main_window::update_res_to_func_list(int r, Dialog *dlg)
{
    if(!dlg->is_canceled)
    {
        remove_from_listview(r);
        add_res_to_func_list(dlg);
    }
}

void main_window::remove_from_listview(int row)
{
   QTextEdit *item = (QTextEdit *)ui->func_list->cellWidget(row, 0);
   reove_from_map(item->toPlainText());
   reove_from_list(row);
   delete item;
   ui->func_list->removeRow(row);
}

void main_window::on_rm_func_clicked()
{
   remove_from_listview(ui->func_list->currentRow());
}

void main_window::on_edit_bt_clicked()
{
    edit_item(nullptr);
}

void main_window::on_view_bt_clicked()
{
    QString last_path=".";
    if(ui->xml_path->text()!="")
    {
        last_path = ui->xml_path->text();
    }
    QString path = QFileDialog::getOpenFileName(this, tr("Open .xml"), last_path, tr("xml Files(*.xml)"));
    if (path.length() == 0)
    {
        alert("您找不到对象");
        return;
    }
    else
    {
        ui->xml_path->setText(path);
    }
}

void main_window::on_view_bt_cli_clicked()
{
    QString last_path=".";
    if(ui->cli_path->text()!="")
    {
        last_path = ui->cli_path->text();
    }
    QString path = QFileDialog::getExistingDirectory(this,QString(),last_path);
    if (path.length() == 0)
    {
        alert("您找不到对象");
        return;
    }
    else
    {
        ui->cli_path->setText(path);
    }
}

void main_window::on_view_bt_server_clicked()
{
    QString last_path=".";
    if(ui->cli_path->text()!="")
    {
        last_path = ui->server_path->text();
    }
    QString path = QFileDialog::getExistingDirectory(this,QString(),last_path);
    if (path.length() == 0)
    {
        alert("您找不到对象");
        return;
    }
    else
    {
        ui->server_path->setText(path);
    }
}

void main_window::on_load_xml_clicked()
{
    if(is_xml_empty())
    {
        alert("xml不能为空");
        return;
    }
    clear();
    load_file(ui->xml_path->text());
}

void main_window::on_save_xml_clicked()
{
    if(is_xml_empty())
    {
        alert("xml不能为空");
        return;
    }
    save_file(ui->xml_path->text());
    alert("保存完毕");
}

void main_window::on_func_list_cellDoubleClicked(int row, int column)
{
    edit_item(nullptr);
}

void main_window::on_generate_clicked()
{
    if(ui->xml_path->text() == "" || ui->cli_path->text() == "" || ui->server_path->text() == "")
    {
        alert("目录不能为空");
        return;
    }
    QString cmd = "/opt/generate_cmd/remote/generate " + ui->xml_path->text() + " \"" + ui->cli_file->text();
    if(ui->comboBox_cli->currentText() == "C++")
    {
        cmd += "*.*\" ";
    }
    else if(ui->comboBox_cli->currentText() == "python")
    {
        cmd += ".py\" ";
    }
    else if(ui->comboBox_cli->currentText() == "python/C++")
    {
        cmd += cmd += "*.*\" ";
    }
    cmd += ui->cli_path->text() + " \"" + ui->serv_file->text()+ "*.*\" " + ui->server_path->text();
    std::string output;
    auto err = buf_exec_cpp(cmd.toStdString(),output);
    if(err)
    {
        alert(QString(output.c_str()));
    }
    else {
        alert("生成成功");
    }
}

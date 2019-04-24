#ifndef MAIN_WINDOW_H
#define MAIN_WINDOW_H

#include "func_dialog.h"

#include <QDomDocument>
#include <QMainWindow>
#include <QStandardItemModel>
#include <QTextEdit>
#include <QXmlStreamWriter>
#include <qlistwidget.h>

namespace Ui {
class main_window;
}

class main_window : public QMainWindow
{
    Q_OBJECT

    std::map<std::string, json_obj> funcs;
private:

     void alert(const QString &str);
     void edit_item(QListWidgetItem *item);
     void add_res_to_func_list(Dialog *dlg);
     void update_res_to_func_list(int r, Dialog *dlg);
     void add_json_to_func(const json_obj & obj);
     void update_funclist_format();
     void update_color(QTextEdit *item);
     void update_color_key_color(QTextEdit *item,const QString &key, const QBrush &brush);
     void add_string_to_func_list(QString &str);

     void clear();
public:
    explicit main_window(QWidget *parent = nullptr);
    ~main_window();

private:

    void remove_from_listview(int row);

     void add_key_to_map(const QString &func_key, const json_obj & obj);
     void reove_from_map(const QString &func_key);

     bool is_xml_empty();

     void recovery_port(QDomNode *node);

     void recovery_project(QDomNode *node);

     void recovery_client(QDomNode *node);

     void recovery_server(QDomNode *node);

     void recovery_func(QDomNode *node);

     void recovery_node(QDomNode *node);

     void recovery(QDomDocument *doc);

     void load_file(const QString &path);

     void save_file(const QString &path);

     void save_port(QXmlStreamWriter *writer);

     void save_project(QXmlStreamWriter *writer);

     void save_client(QXmlStreamWriter *writer);

     void save_server(QXmlStreamWriter *writer);

     void save_params(QXmlStreamWriter *writer, const json_obj &obj);

     void save_func(QXmlStreamWriter *writer);

     void save(QXmlStreamWriter *writer);

private slots:
    void on_add_func_clicked();

    void on_rm_func_clicked();

    void on_edit_bt_clicked();

    void on_view_bt_clicked();

    void on_view_bt_cli_clicked();

    void on_view_bt_server_clicked();

    void on_load_xml_clicked();

    void on_save_xml_clicked();

    void on_func_list_cellDoubleClicked(int row, int column);

    void on_generate_clicked();

private:
    Ui::main_window *ui;
};

#endif // MAIN_WINDOW_H

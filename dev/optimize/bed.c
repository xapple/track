#include <Python.h>
#include <sqlite3.h>

static PyObject* to_sql(PyObject* self, PyObject* args){
    printf("The C test is working\n");
    return Py_BuildValue("");
}

/* ------------------------------------------------------------ */
static PyMethodDef ModuleMethods[] = {
    /* Declare all the module's functions */
    {"to_sql", to_sql, METH_VARARGS, "Convert a BED to SQL"},
    {NULL, NULL, 0, NULL}};

PyMODINIT_FUNC initbed(void){
    /* Create the module and add the functions */
    (void) Py_InitModule("bed", ModuleMethods);}

/*
 * The sqlite3.Row object was missing the slice functionality.
 * So I implemented it and submitted a patch.
 *
 * http://bugs.python.org/issue13583
 *
 * In ten or twenty years this patch will have made its
 * way into most python distributions. In the mean time,
 * I packaged my new Row object with the track package.
 * You can use it like this::
 *
 *     import sqlite3
 *     from pyrow import SuperRow
 *     con = sqlit3.connect(":memory:")
 *     con.row_factory = SuperRow
 *
 * The original banner from the row.c file is below.
 */

/* row.c - an enhanced tuple for database rows
 *
 * Copyright (C) 2005-2010 Gerhard Haring <gh@ghaering.de>
 *
 * This file is part of pysqlite.
 *
 * This software is provided 'as-is', without any express or implied
 * warranty.  In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 */


#include <Python.h>
#include "structmember.h"

typedef struct {
    PyObject_HEAD
    PyObject* data;
    PyObject* description;
} SuperRow;

extern PyTypeObject SuperRowType;

static void
SuperRow_dealloc(SuperRow* self)
{
    Py_XDECREF(self->data);
    Py_XDECREF(self->description);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
SuperRow_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    SuperRow *self;
    self = (SuperRow *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int
SuperRow_init(SuperRow *self, PyObject *args, PyObject *kwds)
{
    PyObject *data=NULL, *cursor=NULL, *desc=NULL;

    if (!PyArg_ParseTuple(args, "OO", &cursor, &data)) {
        return -1;
    }

    if (!PyObject_HasAttrString(cursor, "description")) {
        PyErr_SetString(PyExc_TypeError, "instance of cursor required for first argument");
        return -1;
    }

    if (!PyTuple_Check(data)) {
        PyErr_SetString(PyExc_TypeError, "tuple required for second argument");
        return -1;
    }

    Py_INCREF(data);
    self->data = data;

    desc = PyObject_GetAttrString(cursor, "description");
    Py_INCREF(desc);
    self->description = desc;

    return 0;
}

static PyMemberDef SuperRow_members[] = {
    {"data", T_OBJECT_EX, offsetof(SuperRow, data), 0,
     "A tuple containing the actual row"},
    {"description", T_OBJECT_EX, offsetof(SuperRow, description), 0,
     "A description giving the name of each column"},
    {NULL}  /* Sentinel */
};

//############################################################################//
PyObject* SuperRow_subscript(SuperRow* self, PyObject* idx)
{
    long _idx;
    char* key;
    int nitems, i;
    char* compare_key;

    char* p1;
    char* p2;

    PyObject* item;

    if (PyInt_Check(idx)) {
        _idx = PyInt_AsLong(idx);
        item = PyTuple_GetItem(self->data, _idx);
        Py_XINCREF(item);
        return item;
    } else if (PyLong_Check(idx)) {
        _idx = PyLong_AsLong(idx);
        item = PyTuple_GetItem(self->data, _idx);
        Py_XINCREF(item);
        return item;
    } else if (PyString_Check(idx)) {
        key = PyString_AsString(idx);
        nitems = PyTuple_Size(self->description);
        for (i = 0; i < nitems; i++) {
            compare_key = PyString_AsString(PyTuple_GET_ITEM(PyTuple_GET_ITEM(self->description, i), 0));
            if (!compare_key) {
                return NULL;
            }
            p1 = key;
            p2 = compare_key;
            while (1) {
                if ((*p1 == (char)0) || (*p2 == (char)0)) {
                    break;
                }
                if ((*p1 | 0x20) != (*p2 | 0x20)) {
                    break;
                }
                p1++;
                p2++;
            }
            if ((*p1 == (char)0) && (*p2 == (char)0)) {
                /* found item */
                item = PyTuple_GetItem(self->data, i);
                Py_INCREF(item);
                return item;
            }
        }
        PyErr_SetString(PyExc_IndexError, "No item with that key");
        return NULL;
    } else if (PySlice_Check(idx)) {
        Py_ssize_t start, stop, step, slicelength;
        if (PySlice_GetIndicesEx((PySliceObject*)idx,
                         PyTuple_GET_SIZE(self->data),
                         &start, &stop, &step, &slicelength) < 0) {
            return NULL;
        }
        return PyTuple_GetSlice(self->data, start, stop);
    } else {
        PyErr_SetString(PyExc_IndexError, "Index must be int or string");
        return NULL;
    }
}

Py_ssize_t SuperRow_length(SuperRow* self, PyObject* args, PyObject* kwargs)
{
    return PyTuple_GET_SIZE(self->data);
}

static int SuperRow_print(SuperRow* self, FILE *fp, int flags)
{
    return (&PyTuple_Type)->tp_print(self->data, fp, flags);
}

static PyObject* SuperRow_iter(SuperRow* self)
{
    return PyObject_GetIter(self->data);
}

static long SuperRow_hash(SuperRow *self)
{
    return PyObject_Hash(self->description) ^ PyObject_Hash(self->data);
}

static PyObject* SuperRow_richcompare(SuperRow *self, PyObject *_other, int opid)
{
    if (opid != Py_EQ && opid != Py_NE) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }
    if (PyType_IsSubtype(Py_TYPE(_other), &SuperRowType)) {
        SuperRow *other = (SuperRow *)_other;
        PyObject *res = PyObject_RichCompare(self->description, other->description, opid);
        if ((opid == Py_EQ && res == Py_True)
            || (opid == Py_NE && res == Py_False)) {
            Py_DECREF(res);
            return PyObject_RichCompare(self->data, other->data, opid);
        }
    }
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
}

PyObject* SuperRow_keys(SuperRow* self, PyObject* args, PyObject* kwargs)
{
    PyObject* list;
    int nitems, i;

    list = PyList_New(0);
    if (!list) {
        return NULL;
    }
    nitems = PyTuple_Size(self->description);

    for (i = 0; i < nitems; i++) {
        if (PyList_Append(list, PyTuple_GET_ITEM(PyTuple_GET_ITEM(self->description, i), 0)) != 0) {
            Py_DECREF(list);
            return NULL;
        }
    }

    return list;
}

//############################################################################//
static PyMethodDef SuperRow_methods[] = {
    {"keys", (PyCFunction)SuperRow_keys, METH_NOARGS,
     "Returns the keys of the row."
    },
    {NULL}  /* Sentinel */
};

PyMappingMethods SuperRow_as_mapping = {
     (lenfunc)SuperRow_length,       /*mp_length*/
     (binaryfunc)SuperRow_subscript, /*mp_subscript*/
     (objobjargproc)0,               /*mp_ass_subscript*/
};

PyTypeObject SuperRowType = {
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
    "pyrow.SuperRow",                         /* tp_name */
    sizeof(SuperRow),                         /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)SuperRow_dealloc,             /* tp_dealloc */
    (printfunc)SuperRow_print,                /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0,                                        /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    &SuperRow_as_mapping,                     /* tp_as_mapping */
    (hashfunc)SuperRow_hash,                  /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "SuperRow objects",                       /* tp_doc */
    (traverseproc)0,                          /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)SuperRow_richcompare,        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    (getiterfunc)SuperRow_iter,               /* tp_iter */
    0,                                        /* tp_iternext */
    SuperRow_methods,                         /* tp_methods */
    SuperRow_members,                         /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)SuperRow_init,                  /* tp_init */
    0,                                        /* tp_alloc */
    SuperRow_new,                             /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC /* declarations for import and export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initpyrow(void)
{
    PyObject* m;

    if (PyType_Ready(&SuperRowType) < 0)
        return;

    m = Py_InitModule3("pyrow", module_methods,
                       "Replacement for the sqlite.Row object.");

    if (m == NULL)
      return;

    Py_INCREF(&SuperRowType);
    PyModule_AddObject(m, "SuperRow", (PyObject *)&SuperRowType);
}

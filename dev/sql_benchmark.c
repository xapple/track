// gcc sql_readwrite.c -lsqlite3 -o c_readwrite 
// time c_readwrite 
 
#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>

int main(void){
    int r;
    char* errmsg;
    sqlite3* conW;
    sqlite3* conR;
    r = sqlite3_open("/scratch/sinclair/tmp/write_database.sql", &conW);
    if(r) {printf("Can't open db: %s\n", sqlite3_errmsg(conW)); exit(1);}
    r = sqlite3_open("/scratch/sinclair/tmp/read_database.sql", &conR);
    if(r) {printf("Can't open db: %s\n", sqlite3_errmsg(conR)); exit(1);}
    r = sqlite3_exec(conW, "BEGIN", 0, 0, &errmsg);
    if(r!=SQLITE_OK) {printf("Can't start transaction: %s\n", errmsg); exit(1);}
    char *tables[]={ "table0",
                     "table1",
                     "table2",
                     "table3",
                     "table4",
                     "table5",
                     "table6",
                     "table7",
                     "table8",
                     "table9"};
    int n = 10;
    int j = 0;
    int i;
    char queryR[1024];
    char queryW[1024];
    sqlite3_stmt* stmR;
    sqlite3_stmt* stmW;
    for(i=0; i<n; i++){
        snprintf(queryW, sizeof(queryW), "%s%s%s", "CREATE table '", tables[i], "' (one text, two text, three integer)");
        r = sqlite3_exec(conW, queryW, 0, 0, &errmsg);
        if(r!=SQLITE_OK) {printf("Can't execute: %s\n", errmsg); exit(1);}

        snprintf(queryR, sizeof(queryR), "%s%s%s", "SELECT * from '", tables[i], "'");
        r = sqlite3_prepare_v2(conR, queryR, -1, &stmR, 0);
        if(r!=SQLITE_OK) {printf("Can't prepare read: %s\n", sqlite3_errmsg(conR)); exit(1);}

        snprintf(queryW, sizeof(queryW), "%s%s%s", "INSERT into '", tables[i], "' values (?,?,?)");
        r = sqlite3_prepare_v2(conW, queryW, -1, &stmW, 0);
        if(r!=SQLITE_OK) {printf("Can't prepare write: %s\n", sqlite3_errmsg(conW)); exit(1);}
        while (1){
            j++;
            r = sqlite3_step(stmR);
            if (r == SQLITE_DONE) {break;}
            if (r != SQLITE_ROW) {printf("Can't step read statement (%d): %s\n", r, sqlite3_errmsg(conR)); exit(1);}
            
            r = sqlite3_bind_text(stmW, 1, sqlite3_column_text(stmR, 0), 6, 0);
            if(r!=SQLITE_OK) {printf("Row %d, can't bind first var of write statement (%d): %s\n",  j, r, sqlite3_errmsg(conW)); exit(1);}
            r = sqlite3_bind_text(stmW, 2, sqlite3_column_text(stmR, 1), 6, 0); 
            if(r!=SQLITE_OK) {printf("Row %d, can't bind second var of write statement (%d): %s\n", j, r, sqlite3_errmsg(conW)); exit(1);}
            r = sqlite3_bind_int( stmW, 3, sqlite3_column_int( stmR, 2) +1); 
            if(r!=SQLITE_OK) {printf("Row %d, can't bind third var of write statement (%d): %s\n",  j, r, sqlite3_errmsg(conW)); exit(1);}
            
            r = sqlite3_step(stmW);
            if(r!=SQLITE_DONE) {printf("Can't step on write statement (%d): %s\n", r, sqlite3_errmsg(conW)); exit(1);}
            r = sqlite3_reset(stmW);
            if(r!=SQLITE_OK) {printf("Can't reset the write statement (%d): %s\n", r, sqlite3_errmsg(conW)); exit(1);}}}
     sqlite3_close(conR);
     r = sqlite3_exec(conW, "COMMIT", 0, 0, &errmsg);
     if(r!=SQLITE_OK) {printf("Can't commit transaction: %s\n", errmsg); exit(1);}
     sqlite3_close(conW); 
     return 0;}

#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<regex.h>

struct Diff_data
{
	char *info_file_name; 
	char **diff_line_info;
} diff_data;


// 获取文件内容
char * get_file_content(const char *fname);
// 解析diff文件
void parse_diff_file(char *file_name);

int main(int argc,char* argv[])
{
    if (argc > 1) {
		char *fpath = argv[1];
		char *file_name = NULL;
        int sep = '/';
        if (fpath != NULL) {
            file_name = strrchr(fpath, sep);
        }
        if (file_name == NULL) {
            file_name = fpath;
        } else {
            file_name = file_name + 1;
        }
        unsigned long right_name_len = strlen(file_name) - strlen(".txt");
        char right_name[right_name_len];
		strncpy(right_name, file_name, strlen(file_name) - strlen(".txt"));
        right_name[right_name_len - 1] = '\0';
		printf("1%s\n", right_name);
        
		diff_data.info_file_name = strcat(file_name, "_test.info");

        char *diff_content = get_file_content(fpath);
        char *version = argc > 2 ? argv[2] : "0";
		printf("diff_content:\n%s",diff_content);

		parse_diff_file(diff_content);
    }
    return 0;
}

// 获取文件内容
char * get_file_content(const char *fname)
{
	FILE *fp;
	char *str;
	char txt[1000];
	int file_size;
	if ((fp = fopen(fname, "r")) == NULL) {
		printf("打开文件%s错误\n",fname);
		return NULL;
	}
 
	fseek(fp,0,SEEK_END); 
 
	file_size = ftell(fp);
	str = (char *)malloc(file_size);
	str[0] = 0;
 
	rewind(fp);
	while((fgets(txt,1000,fp)) != NULL) {
		strcat(str,txt);
	}
	fclose(fp);
	return str;
}

char * match_regex(const char *pattern, const char *user_string)
{
    char *result = "";

    regex_t regex;
    int regexInit = regcomp( &regex, pattern, REG_EXTENDED );
    if( regexInit )
    {
        //Error print : Compile regex failed
    }
    else
    {
		regmatch_t p_match[1]; 
        int reti = regexec( &regex, user_string, 0, p_match, 0 );
        if( REG_NOMATCH == reti )
        {
            //Error print: match failed! 
        }
        else
        {
			for (int i = p_match[0].rm_so; i < p_match[0].rm_eo; i++)
				strcat(result, user_string[i]);
        }
    }
    regfree( &regex );
    return result;
}

// 解析diff文件
void parse_diff_file(char *file_name)
{	
	char *diff_content = get_file_content(file_name);
	char *line_content;
	line_content = strtok(diff_content, "\n");
	while (line_content != NULL)
	{
		char *diff_line_info = match_regex("^@@*$@@", line_content);
		if (diff_line_info != NULL)
		{
			printf("========== %s ===========\n", diff_line_info);
		}
		line_content = strtok(NULL, "\n");
	}
	
}


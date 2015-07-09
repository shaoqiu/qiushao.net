在linux下，sublime text默认不能输入中文，搜索了一下，找到了以下的解决方案。
**测试环境:ubuntu 15.04**

### 1.安装fcitx输入法
```
sudo apt-get install fcitx fcitx-table-wbpy
```

[下载搜狗拼音输入法](http://pinyin.sogou.com/linux/?r=pinyin)
安装搜狗拼音输入法:
```
sudo dpkg -i sogoupinyin_1.2.0.0042_amd64.deb
#上面的安装方法可能会出现依赖问题而导致安装错误，
#这时只要执行以下命令就可以自动解决依赖问题，修复安装错误
sudo apt-get install -f
```

安装完成后还得配置一下：
`system setting` --> `language support` --> `keyboard input method system` 中选择 `fcitx`
如果系统还没有安装中文的话，还得安装中文支持先。
重启系统应该输入法框架就会切换为fcitx了。但这时还没有加入中文输入法，需要手动添加。
右击输入法图标 --> 配置 --> 点出左下角的`+` ，选择需要添加的输入法，按OK即可。
需要注意的是如果系统语言是英文的话，要取消`only show current language` 复选框才行。否则是不会显示中文输入法的。


### 2.安装sublime text 补丁
新建文件sub-fcitx.c, 将下面的代码复制进去 
```c
/*
   sublime-imfix.c
   Use LD_PRELOAD to interpose some function to fix sublime input method support for linux.
   By Cjacker Huang
   gcc -shared -o libsublime-imfix.so sublime-imfix.c `pkg-config --libs --cflags gtk+-2.0` -fPIC
   LD_PRELOAD=./libsublime-imfix.so subl
   */
#include <gtk/gtk.h>
#include <gdk/gdkx.h>
typedef GdkSegment GdkRegionBox;
struct _GdkRegion
{
    long size;
    long numRects;
    GdkRegionBox *rects;
    GdkRegionBox extents;
};
GtkIMContext *local_context;
    void
gdk_region_get_clipbox (const GdkRegion *region,
        GdkRectangle *rectangle)
{
    g_return_if_fail (region != NULL);
    g_return_if_fail (rectangle != NULL);
    rectangle->x = region->extents.x1;
    rectangle->y = region->extents.y1;
    rectangle->width = region->extents.x2 - region->extents.x1;
    rectangle->height = region->extents.y2 - region->extents.y1;
    GdkRectangle rect;
    rect.x = rectangle->x;
    rect.y = rectangle->y;
    rect.width = 0;
    rect.height = rectangle->height;
    //The caret width is 2;
    //Maybe sometimes we will make a mistake, but for most of the time, it should be the caret.
    if(rectangle->width == 2 && GTK_IS_IM_CONTEXT(local_context)) {
        gtk_im_context_set_cursor_location(local_context, rectangle);
    }
}
//this is needed, for example, if you input something in file dialog and return back the edit area
//context will lost, so here we set it again.
static GdkFilterReturn event_filter (GdkXEvent *xevent, GdkEvent *event, gpointer im_context)
{
    XEvent *xev = (XEvent *)xevent;
    if(xev->type == KeyRelease && GTK_IS_IM_CONTEXT(im_context)) {
        GdkWindow * win = g_object_get_data(G_OBJECT(im_context),"window");
        if(GDK_IS_WINDOW(win))
            gtk_im_context_set_client_window(im_context, win);
    }
    return GDK_FILTER_CONTINUE;
}
void gtk_im_context_set_client_window (GtkIMContext *context,
        GdkWindow *window)
{
    GtkIMContextClass *klass;
    g_return_if_fail (GTK_IS_IM_CONTEXT (context));
    klass = GTK_IM_CONTEXT_GET_CLASS (context);
    if (klass->set_client_window)
        klass->set_client_window (context, window);
    if(!GDK_IS_WINDOW (window))
        return;
    g_object_set_data(G_OBJECT(context),"window",window);
    int width = gdk_window_get_width(window);
    int height = gdk_window_get_height(window);
    if(width != 0 && height !=0) {
        gtk_im_context_focus_in(context);
        local_context = context;
    }
    gdk_window_add_filter (window, event_filter, context);
}
```

安装编译环境：
```
sudo apt-get install build-essential
sudo apt-get install libgtk2.0-dev
```

编译生成so文件:
```
gcc -shared -o libsublime-imfix.so sub-fcitx.c `pkg-config --libs --cflags gtk+-2.0` -fPIC
```

正常的话，目录下会多一个libsublime-imfix.so文件。将这个文件COPY到sublime text所在的目录。
```
sudo cp libsublime-imfix.so /opt/sublime_text/
```

### 3.配置启动方式：
切换到 `/opt/sublime_text` 目录, 执行：
```
LD_PRELOAD=./libsublime-imfix.so ./sublime_text
```

一般来说，这样启动sublime text就能输入中文了，但是比较麻烦，而且我一般都是从dash启动的。
所以得配置一下sublime text 通过dash启动的方式。
```
sudo vim /usr/share/applications/sublime_text.desktop
```

将`[Desktop Entry]`中的字符串
```
Exec=/opt/sublime_text/sublime_text %F
```

修改为
```
Exec=bash -c "LD_PRELOAD=/opt/sublime_text/libsublime-imfix.so exec /opt/sublime_text/sublime_text %F"
```

将`[Desktop Action Window]`中的字符串
```
Exec=/opt/sublime_text/sublime_text -n
```

修改为
```
Exec=bash -c "LD_PRELOAD=/opt/sublime_text/libsublime-imfix.so exec /opt/sublime_text/sublime_text -n"
```

将`[Desktop Action Document]`中的字符串
```
Exec=/opt/sublime_text/sublime_text --command new_file
```

修改为
```
Exec=bash -c "LD_PRELOAD=/opt/sublime_text/libsublime-imfix.so exec /opt/sublime_text/sublime_text --command new_file"
```

如此便完美解决了sublime text的中文输入问题了。
# Coding=utf-8
import csv

# 定义全局变量并初期化
current_room = '密室'  # 当前房间

inventorys = []  # 随身物品的列表

game_over = False  # 游戏结束标志
"""
False:游戏没有终止，可以继续进行
True:游戏已经终止
"""
rooms = {}  # 房间的属性字典
"""
rooms的结构如下：
    rooms = {
        room_id: {
            'east': 'xxx'  # 东面房间的ID
            'east_lock': 'xxx'  # 东面房间上锁的状态
                                  'unlock': 未上锁
                                  '钥匙ID': 上锁，可用钥匙'钥匙ID'打开房门
            'south': 'xxx'  # 南面房间的ID
            'south_lock': 'xxx'  # 南面房间上锁的状态
            'west': 'xxx'  # 西面房间的ID
            'west_lock': 'xxx'  # 西面房间上锁的状态
            'north': 'xxx'  # 北面房间的ID
            'north_lock': 'xxx'  # 北面房间上锁的状态
            'item': 'xxx'  # 当前房间内可获取的物品
            'monster': 'xxx'  # 当前房间内的怪兽名称
            'goal': 'xxx'  # 当前房间是否为终点。终点的值为'1'
        },
        ……
        ……
    }
"""
hunt = {}  # 各种怪兽的对策字典
"""
hunt的结构如下：
    hunt = {
        monster_id: {
            'weapon': 'xxx'  # 可以克制该怪兽的武器/物品名称
            'success': 'xxx'  # 杀怪成功时提示的信息
            'failed': 'xxx'  # 杀怪失败时提示的信息
        },
        ……
        ……
    }
"""
msg = {}  # 输出信息字典
"""
msg的结构如下：
    msg = {
        msg_id: {
            'msg_desc': 'xxx'  # 信息模板
        },
        ……
        ……
    }
"""
game_info = {'rooms':rooms, 'hunt':hunt, 'msg':msg}  # 游戏信息字典

directions = ['east', 'south', 'west', 'north']  # 方位列表

action = {}  # 指令与执行函数的映射字典


def main():
    """游戏的主处理.

    以循环的方式等待玩家输入指令，进行指令合法性检查，然后调用指令对应的处理函数。
    直到玩家到达终点或者被怪兽杀死，游戏结束。
    Args:
    Returns:
    Raises:
    """
    init()  # 调用初期处理
    do_look('')  # 调用观察当前房间的函数，输出初始位置的环境信息
    while not game_over:  # 游戏引擎，执行循环直到游戏结束
        cmd = input('接下来你想做什么？请输入:')  # 提示玩家输入行动指令
        
        # 为了方便对玩家输入的指令进行处理，需要对输入内容进行整形（全部统一为小写字母)
        # 对指令以空格为间隔，分割为指令列表（['动作','方向/对象']）
        cmd = cmd.lower().split()  # 获得指令列表

        # 行动指令未输入，或者参数过多，或者输入的‘动作’不在处理对象范围内
        # 都是无效行动指令，不能被正常识别
        if len(cmd) == 0 or len(cmd) > 2 or not cmd[0] in action:  # 指令合法性检查
            output_msg('msg_err', '')  # 提示输入的行动指令无效
        else:
            # 'look'和'exit'都是没有动作对象的动作，指令输入只有‘动作’，
            # 为了统一动作处理函数的调用方法,需要在指令列表中以空格补足'方向/对象'
            if cmd[0] == 'look' or cmd[0] == 'exit':  # 指令动作为'look'或者'exit'
                cmd += ' '  # 以空格补足'方向/对象'

            # 利用“指令与执行函数的映射字典（action）”实现类似swich-case语句的功能。
            # 以指令中的动作（cmd[0]）作为key，获得对应的处理函数名称。
            # 并以指令中的对象/方向(cmd[1])为参数，调用相应的函数。
            # 该过程中会通过改变game_over的值结束游戏。
            action.get(cmd[0])(cmd[1])  # 执行输入的动作指令
            output_inventorys()  # 提示当前随身物品列表

def init():
    """初期处理.

    用于对游戏的初始信息（地图，怪兽，输出信息等）进行加载，并输出游戏的欢迎信息
    Args:
    Returns:
    Raises:
    """
    global action
    load_map('map.csv', 'rooms')  # 导入地图定义文件，构建房间的属性集合
    load_file('monster.csv', 'hunt')  # 导入怪兽定义文件，构建怪兽的对策集合
    load_file('msg.csv', 'msg')  # 导入信息定义文件，构建输出信息的集合

    # 输出欢迎信息
    output_msg('msg_welcome', '')

    # 命令执行函数映射初期化
    action = {'go':do_go, 'get':do_get, 'look':do_look, 'exit':do_exit}

def font_red(words):
    """红色字体设定函数.

    用于将参数中的可变部分（'%%'）以外内容设为红色字体。
    Args:
        words:需要设定的颜色的对象字符串。
            该字符串为输出信息的模板，其中可变部分以'%%'表示。
            例如:'我向%%走去。'
            运行时根据需要可以将'%%'替换成相应的具体位置（如:客厅）
    Returns:
        返回追加颜色控制字符后的字符串。
        控制台文字颜色的控制字符如下:
            格式:\033[显示方式;前景色;背景色m
            说明:
            前景色            背景色           颜色
            ---------------------------------------
            30                40              黑色
            31                41              红色
            32                42              绿色
            33                43              黃色
            34                44              蓝色
            35                45              紫红色
            36                46              青蓝色
            37                47              白色
            显示方式           意义
            -------------------------
            0                终端默认设置
            1                高亮显示
            4                使用下划线
            5                闪烁
            7                反白显示
            8                不可见

            例子:
            \033[1;31;40m    <!--1-高亮显示 31-前景色红色  40-背景色黑色-->
            \033[0m          <!--采用终端默认设置，即取消颜色设置-->
    Raises:
    """
    return ('\033[1;31;40m' + words.replace('%%',
        '\033[0m%%\033[1;31;40m') + '\033[0m')

def font_green(words):
    """绿色字体设定函数.

    用于将参数中的字符串设为绿色字体。
    Args:
        words:需要设定的颜色的对象字符串。
            该字符串为输出信息中的可变部分。
    Returns:
        返回追加颜色控制字符后的字符串。
    Raises:
    """
    return '\033[1;32;40m' + words + '\033[0m'

def output_msg(msg_id, msg_keyword):
    """信息输出函数.

    根据参数中的msg_id获得相应的信息模板，并用msg_keyword的内容，
    替换模板中的可变部分后输出。输出内容中，固定部分设为红色字体，可变部分设为绿色字体。
    Args:
        msg_id:信息模板的ID。可以作为key从输出信息字典中取得相应的信息模板。
            该字符串为输出信息中的可变部分。
        msg_keyword:用于替换可变部分的文字列。
    Returns:
        将处理后的信息内容输出到控制台。
    Raises:
    """
    if msg_keyword == '':  # 判断是否存在可变部分
        # 不存在可变化内容时，将msg_id指定的信息内容以红色字体输出
        print(font_red(msg[msg_id]['msg_desc']))
    else:
        # 存在可变化内容时，使用msg_keyword指定的内容，
        # 替换msg_id对应的信息模板中的‘%%’，并输出。
        # 其中，msg_keyword的内容以绿色字体输出，模板中固定内容以红色字体输出。
        print(font_red(msg[msg_id]['msg_desc']).replace('%%',
            font_green(msg_keyword)))

def output_inventorys():
    """随身物品列表输出函数.

    将随身物品列表输出到控制台。
    Args:
    Returns:
    Raises:
    """
    global inventorys
    if len(inventorys) ==0:  # 判断列表是否为空
        output_msg('msg_no_inventory', '')  # 提示没有物品
    else:
        s = ','
        output_msg('msg_list', s.join(inventorys))  # 提示物品清单

def load_map(file_name, info_type='rooms'):
    """导入地图文件函数.

    根据file_name指定的文件名，导入地图文件，并构建用于保存地图信息的字典数据。
    该函数只将有值的属性添加到属性字典中，例如:
        rooms = {
            'room1': {
                'south': 'room2'
                'south_lock': 'unlock'
                'item': 'key1'
            },
            'room2': {
                'north': 'room1'
                'north_lock': 'unlock'
                'east': 'room3'
                'east_lock': 'key1'
            },
            ……
            ……
        }
    Args:
        file_name:保存地图数据的文件名。
        info_type:信息类型，用于确定游戏信息字典的对象名称。默认为'rooms'
    Returns:
    Raises:
    """
    global game_info
    with open(file_name) as file_obj:  # 打开参数(file_name)指定的定义文件
        title_line = file_obj.readline()  # 读入标题行
        title_line = title_line.rstrip('\n').split(',')  # 取得各个项目的标题列表
        # 继续读入各明细行(每行对应一个房间的属性)的定义内容，并根据读入内容建立字典
        for line in file_obj:  
            line = line.rstrip('\n').split(',')  # 获得当前房间的属性列表
            info_id = line[0]  # 取得房间的名称（字典的Key）
            del line[0]  # 从属性列表中删除Key项目，保留其他属性项目作为字典的Value
            game_info.get(info_type)[info_id] = {}  # 以子字典类型作为字典的Value
            index = 1  # 标题行中，对应的属性名称的列表索引，初期化为1（0为房间名称）
            # 将当前行中的每个非空项目，作为当前房间的属性，添加到子字典中。
            # 以标题行对应位置的内容作为Key,当前行的项目内容作为Value。
            for value in line:
                if value == '':
                    pass  # 空项目不添加
                else:
                    # 添加字典的项目
                    game_info.get(info_type)[info_id][
                        title_line[index]] = value
                index += 1

def load_file(file_name, info_type):
    """游戏信息导入函数.

    根据file_name指定的CSV文件名，导入游戏数据信息，并构建用于保存信息的字典数据。
    该函数将CSV中所有列都作为属性添加到属性字典中，例如:
        hunt = {
            'monster1': {
                'weapon': 'weapon1'
                'success': 'success_msg1'
                'failed': 'failed_msg1'
            },
            'monster2': {
                'weapon': 'weapon2'
                'success': 'success_msg2'
                'failed': 'failed_msg2'
            },
            ……
            ……
        }
    这种情况利用csv的开源包实现，程序可以更加简洁。
    Args:
        file_name:游戏数据信息的CSV文件名。
        info_type:信息类型,用于确定游戏信息字典的对象名称。
    Returns:
    Raises:
    """
    global game_info
    with open(file_name, 'r') as csvFile:  # 打开参数(file_name)指定的csv文件
        dict_reader = csv.DictReader(csvFile)  # 以字典方式读入csv文件
        for line in dict_reader:  # 以字典形式取得每一个明细行的内容
            info_id = line['id']  # 取得当前明细行的'id'，作为游戏信息字典的Key
            del line['id']  # 删除Key项目，保留其他属性项目作为字典的Value
               # 有多个属性的场合，以取得的字典作为游戏信息字典的Value
            game_info.get(info_type)[info_id] = line 

def do_exit(tmp):
    """游戏终止函数.

    将游戏结束标志设为True，使主函数（main）的循环满足终止条件。
    Args:
        tmp:没有具体用途，只是为了统一动作指令的处理函数的形式。
    Returns:
    Raises:
    """
    global game_over
    game_over = True

def do_opendoor(direction):
    """开门动作处理函数.

    用于执行开门动作的处理。该函数为移动命令处理函数自动发起执行。
    该函数会检验参数中指定的方向的房门是否上锁。
    上锁的场合，确认随身物品中是否有匹配的钥匙。
    有钥匙或未上锁，则开门进入下一个房间。否则提示相应的信息。
    Args:
    　　　　direction:玩家指令中指定的希望移动的方向
    Returns:
    Raises:
    """
    global current_room, inventorys, rooms
    # 获得参数direction指定方向的房门上锁状态，未上锁时取得‘unlock’，
    # 上锁是去的匹配的钥匙名称
    key = rooms[current_room][direction + '_lock']
    if key == 'unlock':  # 判断是否上锁
        # 没有上锁的场合
        current_room = rooms[current_room][direction]  # 进入下一个房间
        do_look('')  # 观察一下新房间的情况
    else:
        # 房间上锁的场合
        output_msg('msg_lock', '')  # 提示玩家该房门被锁
        if key in inventorys:  # 判断身上是否有匹配的钥匙
            # 有匹配的钥匙的场合
            output_msg('msg_opendoor', key)  # 输出开门信息
            rooms[current_room][direction + '_lock'] = 'unlock'  # 将该房门的上锁状态改为‘unlock’
            del inventorys[inventorys.index(key)]  # 从随身物品列表中删除已经使用过的钥匙
            current_room = rooms[current_room][direction]  # 进入下一个房间
            do_look('')  # 观察一下新房间的情况
        else:
            # 身上没有匹配钥匙的场合
            output_msg('msg_nokey', '')  # 提示没有钥匙的信息

def do_go(direction):
    """移动命令处理函数.

    用于执行玩家输入的移动指令。
    该函数会检验参数中指定的方向是否存在当前房间出口。
    存在的场合，调用开门处理函数实现移动动作。
    Args:
    　　　　direction:玩家指令中指定的希望移动的方向
    Returns:
    Raises:
    """
    global current_room, rooms
    # 判断参数指定的方向是否在于当前房间的可移动范围内
    if not direction in rooms[current_room]:
        # 不是当前房前的可移动的方向的场合
        if direction in directions:  # 判断参数是否为一个合法的‘方向’
            # 是合法的‘方向’说明，说明指定方向没有出口
            output_msg('msg_go', direction)  # 提示向指定方向移动
            output_msg('msg_noway', '')  # 提示没有出口
        else:
            # 不是正常的方向的场合
            output_msg('msg_err', '')  # 提示指令错误
    else:
        # 参数（direction）指定的移动方向是当前房间可移动方向范围内的时候
        output_msg('msg_go', direction)  # 提示向指定方向移动
        do_opendoor(direction)  # 执行开门动作

def do_get(item):
    """获取物品命令处理函数.

    用于执行玩家输入的获取物品的指令。
    该函数会检验参数中指定的物品在当前房间内是否存在。
    存在的场合，将该物品追加到随身物品的列表中。
    Args:
    　　　　ｉｔｅｍ:玩家指令中指定的希望得到的物品名称
    Returns:
    Raises:
    """
    global inventorys, current_room, rooms
    # 确认参数中指定的物品是否存在于当前房间
    if 'item' in rooms[current_room] and item == rooms[current_room]['item']:
        # 当前房间有可获取的物品，并且物品的名称与动作对象（item）吻合的场合
        output_msg('msg_get', item)  # 提示获得物品的信息
        inventorys.append(item)  # 将该物品追加到随身物品列表中
        del rooms[current_room]['item']  # 从当前房间的属性中删除该物品
    else:
        # 该物品不存在于当前房间的场合
        output_msg('msg_noitem', '')  # 输出物品不存在的信息

def kill_monster():
    """打怪兽命令处理函数.

    打怪兽指令只在进入一个新的房间后被自动执行。
    如果遇到怪兽，则判断随身物品中是否有克制怪兽的特定物品。如果有则自动使用物品克制怪兽，
    没有的话，则会被怪兽杀死，游戏结束。
    Args:
    Returns:
        返回玩家是否还活着的状态。
        True:活着，可以继续游戏
        False:已挂，不能继续游戏
    Raises:
    """
    global current_room, rooms, hunt, inventorys

    if 'monster' in rooms[current_room]:  # 当前房间中是否存在怪兽
        monster = rooms[current_room]['monster']  # 获取该怪兽的名字
        output_msg('msg_monster', monster) # 提示存在怪兽的信息
        weapon = hunt[monster]['weapon']  # 获取克制该怪兽的物品名称
        if weapon in inventorys:  # 检查随身物品中是否有克制怪兽的物品
            # 当随身带有克制怪兽的物品的场合
            print(font_red(hunt[monster]['success']))  # 提示打败怪兽
            del inventorys[inventorys.index(weapon)]  # 从随身物品列表中删除已经使用的物品
            del rooms[current_room]['monster']  # 删除当前房间的怪兽
            return True  # 玩家还活着
        else:
            # 没有带着克制怪兽的物品的场合
            print(font_red(hunt[monster]['failed']))  # 提示被打败的信息
            return False  # 玩家已死
    else:
        return True  # 没有怪兽的场合，玩家当然还活着

def do_look(here):
    """观察命令处理函数.

    用于执行玩家输入的观察指令'look'。
    该函数在玩家进入一个新的房间时会被自动执行。
    通过该函数将实现如下功能:
        1、确认新的房间是否为终点
        2、确认房间内是否有怪兽，有怪兽的时候自动进行战斗
        3、确认房间内是否有物品，有物品的时候提示玩家
        4、提示玩家当前房间各个方向是否有出路
    Args:
        here:没有具体用途，只是为了统一动作指令的处理函数的形式。
    Returns:
    Raises:
    """
    global current_room, rooms, directions

    output_msg('msg_watch', current_room)  # 提示当前房间名称
    # 判断当前房间是否为游戏终点
    if 'goal' in rooms[current_room] and rooms[current_room]['goal'] == '1':
        # 是终点的场合，结束游戏
        output_msg('msg_win', '')  # 输出胜利信息
        do_exit('')  # 调用游戏终止函数
    else:
        if kill_monster():  # 不是终点的场合，先确认是否存在怪兽
            # 当前房间没有怪兽，或者杀死了怪兽的场合继续游戏
            if 'item' in rooms[current_room]:  # 判断房间内是否有物品
                output_msg('msg_item', rooms[current_room]['item'])  # 输出物品提示信息
            for direction in directions:  # 环顾四周
                if direction in rooms[current_room]:  # 判断某个方向是否有出口
                    output_msg('msg_way', direction)  # 提示当前房间存在的出口
        else:
            # 被怪兽杀死的场合，游戏结束
            do_exit('')  # 调用游戏终止函数

if __name__ == '__main__':
    main()

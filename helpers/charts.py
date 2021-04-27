
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import matplotlib as mpl

def create_pie_chart(labels, data, explode=None, colours=None, rotation=0):
    if not explode:
        explode = [0 for _ in data]
    _, ax1 = plt.subplots()
    tp = {
        "fontsize": 35 + max([len(i) for i in labels]) * -1.25,
        "color": (.9, .9, .9),
        "fontproperties": fm.FontProperties(fname="home/ven/assets/font.ttf")
    }
    ax1.pie(data, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90+rotation, colors=colours, textprops=tp)

    ax1.axis('equal')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True,)
    buf.seek(0)
    return Image.open(buf)


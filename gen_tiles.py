import os
import sys
import webbrowser
import matplotlib.pyplot as plt
from numpy import *
from create_dataset import pointReader as load

freq = 500 # Hz

def init_html(out_dir):
    with open(os.path.join(out_dir, "index.html"), 'w', encoding="utf-8") as header:
        header.write("""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {
  font-family: Helvetica, Calibri, Arial, sans-serif;
  font-weight: bold;
}
div.gallery {
  margin: 5px;
  border: 1px solid #ccc;
  float: left;
  width: 320px;
}

div.gallery:hover {
  border: 1px solid #777;
}

div.gallery img {
  width: 100%;
  height: auto;
}

div.desc {
  padding: 15px;
  text-align: center;
}
</style>
</head>
<body>
""")

def to_gallery(out_dir, spoint, epoint, src_file_id):
    filename = str(src_file_id) + "_" + str(spoint) + "-" + str(epoint) + ".svg"
    with open(os.path.join(out_dir, "index.html"), 'a', encoding="utf-8") as div:
        div.write("""<div class="gallery">
  <a target="_blank" href="{0}">
    <img src="{1}">
  </a>
  <div class="desc">📈\t{2}—{3}</div>
</div>""".format(filename, filename, str(spoint), str(epoint)))

def finalize_html(out_dir):
    with open(os.path.join(out_dir, "index.html"), 'a', encoding="utf-8") as footer:
        footer.write("""</body>
</html>""")

def gen(dataset, start, end, out_dir, file_sep):
    print("Generating HTML gallery...")

    init_html(out_dir)
    counter = 0
    src_file_id = 0
    for sample in dataset:
        time = 0.000
        time_axis = []
        volt_axis = []
        expected_value = mean(sample)
        for volt in sample:
            volt_axis.append(volt - expected_value)
            time_axis.append(time)
            time += 1/freq
        fig, ax = plt.subplots()
        ax.plot(time_axis, volt_axis)

        if counter in file_sep:
            src_file_id = file_sep.index(counter)

        plt.savefig(os.path.join(out_dir, str(src_file_id) + "_" + str(start[counter]) + "-" + str(end[counter]) + ".svg"), format="svg")
        plt.clf()
        plt.close()
        
        to_gallery(out_dir, start[counter], end[counter], src_file_id)
        counter += 1

    finalize_html(out_dir)
    print("Write [{0}/index.html] FINISHED".format(out_dir))


def main():
    if len(sys.argv) <= 1:
        print("Usage: {0} [pointer file] [output directory]".format(sys.argv[0]))
        return
        
    pointers_file     = sys.argv[1]
    output_dir        = sys.argv[2]

    
    dataset, xxx, yyy, start_points, end_points, file_sep = load(pointers_file)
    os.makedirs(output_dir, exist_ok=True)
    gen(dataset, start_points, end_points, output_dir, file_sep)

    html_file = "file:///" + os.getcwd() + "/" + output_dir + "/index.html"
    webbrowser.open_new_tab(html_file)


if __name__ == '__main__':
    main()
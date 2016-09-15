from svg_wheel import generate_svg_wheel
from utils import (
    annotate_wheels,
    get_top_packages,
    remove_irrelevant_packages,
    save_to_file,
    is_wheel,
    is_platform_specific
)


TO_CHART = 360


def main():
    packages = remove_irrelevant_packages(get_top_packages(), TO_CHART)
    annotate_wheels(packages)
    print("Number of packages: %s" % len(packages))

    wheels = list(filter(is_wheel, packages))
    print("Number of wheels: %s" % len(wheels))

    wheels_platform_specific = list(filter(is_platform_specific, wheels))
    print("Number of platform specific wheels: %s" % len(wheels_platform_specific))

    max_download = wheels_platform_specific[0]['downloads']
    print("Max downloads: %s" % max_download)
    print("Min downloads: %s" % wheels_platform_specific[-1]['downloads'])

    # Now generate some text that can copied into a "world cloud" generator
    for p in wheels_platform_specific:
        percent = p['downloads'] * 100 / max_download
        print((p['name'] + ' ') * int(percent))

    save_to_file(packages, 'results.json')
    generate_svg_wheel(packages, TO_CHART)


if __name__ == '__main__':
    main()

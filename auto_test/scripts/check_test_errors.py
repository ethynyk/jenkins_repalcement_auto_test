import sys
import xml.etree.ElementTree as ET
import os


def count_errors_in_xml(xml_file):
    """统计 XML 报告中的错误数量"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # 方法1: 从 testsuite 的属性获取错误数量
        errors = 0
        for testsuite in root.findall('testsuite'):
            errors += int(testsuite.get('errors', 0))

        # 方法2: 如果没有找到 testsuite 的错误属性，则遍历所有 testcase
        if errors == 0:
            for testcase in root.findall('.//testcase'):
                if testcase.find('error') is not None:
                    errors += 1

        return errors

    except Exception as e:
        print(f"Error parsing XML file {xml_file}: {e}")
        return -1


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_test_errors.py <xml_file>")
        sys.exit(1)

    xml_file = sys.argv[1]

    if not os.path.exists(xml_file):
        print(f"XML file not found: {xml_file}")
        sys.exit(1)

    error_count = count_errors_in_xml(xml_file)
    print(f"Found {error_count} errors in {xml_file}")

    if error_count > 0:
        sys.exit(1)     # exit code 1
    else:
        sys.exit(0)     # exit code 0


if __name__ == "__main__":
    main()

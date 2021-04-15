"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Tokenize the Take Name to a Filename and display how to extract data from a Filename.

Class/method highlighted:
    - c4d.modules.tokensystem.StringExtractRoot()
    - c4d.modules.tokensystem.FilenameExtractRoot()
    - c4d.modules.tokensystem.FilenameSlicePath()

"""
import c4d


def main():

    # Defines a path, with the $take token
    path = '/myprojects/topnotchproject/$take/beautiful.tif'

    # Extracts the root
    root = c4d.modules.tokensystem.StringExtractRoot(path)
    print(root)

    # Gets everything before the first token
    root = c4d.modules.tokensystem.FilenameExtractRoot(path)
    print(root)

    # Splits the path with previous and after the first token
    res = c4d.modules.tokensystem.FilenameSlicePath(path)
    print(res)


if __name__ == '__main__':
    main()

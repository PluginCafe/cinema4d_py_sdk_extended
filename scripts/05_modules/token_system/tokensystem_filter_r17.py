"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Uses the token system to evaluate token with custom variables.

Class/method highlighted:
    - c4d.modules.tokensystem.StringConvertTokensFilter()
    - c4d.modules.tokensystem.FilenameConvertTokensFilter()

"""
import c4d


def main():
    # Defines a path, with the $frame and $prj token
    path = r"/myprojects/topnotchproject/theimage_$frame_$prj.png"
    print(path)

    # Setups the RenderPathData
    rpd = {'_doc': doc, '_rData': doc.GetActiveRenderData(), '_rBc': doc.GetActiveRenderData().GetData(), '_frame': 1}

    # Excludes the project token to the "tokenization"
    exclude = ['prj']

    # Renders token to string
    finalFilename = c4d.modules.tokensystem.StringConvertTokensFilter(path, rpd, exclude)
    print(finalFilename)

    # Renders tokens to string and also change / to \
    finalFilename = c4d.modules.tokensystem.FilenameConvertTokensFilter(path, rpd, exclude)
    print(finalFilename)


if __name__ == '__main__':
    main()

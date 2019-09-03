# Token System

The token system allows the use of expressions in file names. The API makes it possible to handle these tokens.

It is possible to:

  - Use tokens in file names to customize file locations or file names. For example, they could be based on render settings.
  
  - Add custom tokens to be used everywhere in Cinema 4D.

Classic API:
- **c4d.modules.tokensystem**: *The module which provide static methods to use Cinema 4D's Token System.*

## Examples

### tokensystem_filter
Version: R17, R18, R19, R20, R21 - Win/Mac

     Uses the token system to evaluate token with custom variables.

### tokensystem_render
Version: R17, R18, R19, R20, R21 - Win/Mac

    Renders a BaseDocument and saves the resulting image using a filename handling tokens.

### tokensystem_root
Version: R17, R18, R19, R20, R21 - Win/Mac

    Tokenize the Take Name to a Filename and display how to extract data from a Filename.


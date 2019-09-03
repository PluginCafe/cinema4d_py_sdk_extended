CONTAINER pythonpaintbrush
{
  NAME pythonpaintbrush;
  INCLUDE toolsculptbrushbase;
 
    GROUP MDATA_SCULPTBRUSH_SETTINGS_GROUP
    {
        COLUMNS 3;

        GROUP
        {
            COLUMNS 3;
            LONG MDATA_SCULPTBRUSH_SETTINGS_DRAWMODE
            {
                CYCLE
                {
                    MDATA_SCULPTBRUSH_SETTINGS_DRAWMODE_FREEHAND;
                    MDATA_SCULPTBRUSH_SETTINGS_DRAWMODE_LINE;
                    MDATA_SCULPTBRUSH_SETTINGS_DRAWMODE_LASSO_FILL;
                    MDATA_SCULPTBRUSH_SETTINGS_DRAWMODE_POLY_FILL;
                    MDATA_SCULPTBRUSH_SETTINGS_DRAWMODE_RECTANGLE_FILL;
                }
            }
            BOOL MDATA_SCULPTBRUSH_SETTINGS_DRAWMODE_FILL_SYMMETRY { }
            BOOL MDATA_SCULPTBRUSH_SETTINGS_FILL_BACKFACES { }
        }
        STATICTEXT { JOINENDSCALE; }
        STATICTEXT { JOINEND; }

        SEPARATOR { LINE; }
        STATICTEXT { JOINENDSCALE; }
        STATICTEXT { JOINEND; }
    }

}

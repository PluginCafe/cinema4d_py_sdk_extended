CONTAINER Ofalloff_pynoise
{
	NAME Ofalloff_pyrandom;
    INCLUDE Ofalloff_standard;
    
    HIDE FALLOFF_SHAPE_AXIS;
    
    HIDE FALLOFF_SHAPE_SLICE;
    
    HIDE FALLOFF_FUNCTION_RADIUS;
        
    GROUP FALLOFF_GROUPFALLOFF
	{
        GROUP FALLOFF_SETTINGS
		{
            GROUP PYNOISEFALLOFF_SETTINGS
            {
                OPEN;
                
                LONG PYNOISEFALLOFF_SEED { MIN 0; }
                
                LONG PYNOISEFALLOFF_TYPE
                {
                    CYCLE
                    {
                        NOISE_BOX_NOISE;
                        NOISE_BLIST_TURB;
                        NOISE_BUYA;
                        NOISE_CELL_NOISE;
                        NOISE_CRANAL;
                        NOISE_DENTS;
                        NOISE_DISPL_TURB;
                        NOISE_FBM;
                        NOISE_HAMA;
                        NOISE_LUKA;
                        NOISE_MOD_NOISE;
                        NOISE_NAKI;
                        NOISE_NOISE;
                        NOISE_NUTOUS;
                        NOISE_OBER;
                        NOISE_PEZO;
                        NOISE_POXO;
                        NOISE_RANDOM;
                        NOISE_SEMA;
                        NOISE_STUPL;
                        NOISE_TURBULENCE;
                        NOISE_VL_NOISE;
                        NOISE_WAVY_TURB;
                        NOISE_FIRE;
                        NOISE_ELECTRIC;
                        NOISE_GASEOUS;
                        NOISE_CELL_VORONOI;
                        NOISE_DISPL_VORONOI;
                        NOISE_SPARSE_CONV;
                        NOISE_VORONOI_1;
                        NOISE_VORONOI_2;
                        NOISE_VORONOI_3;
                        NOISE_ZADA;
                    }
                }
                
                LONG PYNOISEFALLOFF_SAMPLING
                {
                    CYCLE
                    {
                        SAMPLING_2D;
                        SAMPLING_3D;
                    }
                }
                
                REAL PYNOISEFALLOFF_SAMPRAD { MIN 0; STEP 0.01; }
                REAL PYNOISEFALLOFF_DETATT { MIN 0; STEP 0.01; }
                LONG PYNOISEFALLOFF_REPEAT
                {
                    CYCLE
                    {
                        REPEAT_0;
                        REPEAT_1;
                        REPEAT_3;
                        REPEAT_7;
                        REPEAT_15;
                        REPEAT_31;
                        REPEAT_63;
                        REPEAT_127;
                        REPEAT_255;
                        REPEAT_511;
                        REPEAT_1023;
                    }
                }
                
                REAL PYNOISEFALLOFF_OCTAVES { MIN 0; }
                BOOL PYNOISEFALLOFF_ABSOLUTE {}
                
                GROUP PYNOISEFALLOFF_FBMSETTINGS
                {
                    OPEN;
                    
                    LONG PYNOISEFALLOFF_MAXOCTAVE { MIN 0; }
                    LONG PYNOISEFALLOFF_LACUNARITY { MIN 0; }
                    REAL PYNOISEFALLOFF_H { MIN 0; STEP 0.01; }
                }
            }
        }
    }
}

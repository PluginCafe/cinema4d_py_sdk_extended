#ifndef _Ofalloff_pyrandom_H_
#define _Ofalloff_pyrandom_H_

enum
{
    PYNOISEFALLOFF_SETTINGS    = 7000,
    
    PYNOISEFALLOFF_SEED = 5000,
    PYNOISEFALLOFF_TYPE = 5001,

        NOISE_BOX_NOISE             =  1,
        NOISE_BLIST_TURB            =  2,
        NOISE_BUYA                  =  3,
        NOISE_CELL_NOISE            =  4,
        NOISE_CRANAL                =  5,
        NOISE_DENTS                 =  6,
        NOISE_DISPL_TURB            =  7,
        NOISE_FBM                   =  8,
        NOISE_HAMA                  =  9,
        NOISE_LUKA                  = 10,
        NOISE_MOD_NOISE             = 11,
        NOISE_NAKI                  = 12,
        NOISE_NOISE                 = 13,
        NOISE_NUTOUS                = 14,
        NOISE_OBER                  = 15,
        NOISE_PEZO                  = 16,
        NOISE_POXO                  = 17,
        NOISE_RANDOM                = 18,
        NOISE_SEMA                  = 19,
        NOISE_STUPL                 = 20,
        NOISE_TURBULENCE            = 21,
        NOISE_VL_NOISE              = 22,
        NOISE_WAVY_TURB             = 23,
        NOISE_CELL_VORONOI          = 24,
        NOISE_DISPL_VORONOI         = 25,
        NOISE_SPARSE_CONV           = 26,
        NOISE_VORONOI_1             = 27,
        NOISE_VORONOI_2             = 28,
        NOISE_VORONOI_3             = 29,
        NOISE_ZADA                  = 30,
        NOISE_FIRE                  = 31,
        NOISE_ELECTRIC              = 32,
        NOISE_GASEOUS               = 33,

        NOISE_NONE                  = 99,
    
    PYNOISEFALLOFF_SAMPLING   = 5002,
    
        SAMPLING_2D = 0,
        SAMPLING_3D = 1,
    
    PYNOISEFALLOFF_SAMPRAD = 5003,
    PYNOISEFALLOFF_DETATT  = 5004,
    PYNOISEFALLOFF_REPEAT  = 5005,
        
        REPEAT_0    = 0,
        REPEAT_1    = 1,
        REPEAT_3    = 3,
        REPEAT_7    = 7,
        REPEAT_15   = 15,
        REPEAT_31   = 31,
        REPEAT_63   = 63,
        REPEAT_127  = 127,
        REPEAT_255  = 255,
        REPEAT_511  = 511,
        REPEAT_1023 = 1023,
    
    PYNOISEFALLOFF_OCTAVES  = 5006,
    PYNOISEFALLOFF_ABSOLUTE = 5007,
    
    PYNOISEFALLOFF_FBMSETTINGS = 7001,
    
    PYNOISEFALLOFF_MAXOCTAVE  = 5008,
    PYNOISEFALLOFF_LACUNARITY = 5009,
    PYNOISEFALLOFF_H          = 5010
};

#endif
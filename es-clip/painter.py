#!/usr/bin/env python3
import numpy as np

from PIL import Image, ImageDraw, ImageOps
from shapely.geometry import MultiLineString
from shapely.affinity import rotate, scale, translate
from scipy.ndimage import median_filter, gaussian_filter
from skimage import exposure
import aggdraw

class TrianglesPainter(object):

    def __init__(self, h, w, n_triangle=10, alpha_scale=0.1, coordinate_scale=1.0, aggdraw_=True):
        self.h = h
        self.w = w
        self.n_triangle = n_triangle
        self.alpha_scale = alpha_scale
        self.coordinate_scale = coordinate_scale
        self.aggdraw_ = aggdraw_
        lines = []
        for i in range(0,41,8):
            lines.append([[i,0],[i,40]])
        self.pattern = MultiLineString(lines)
        
        print("painter initiated")
        
    def draw_pattern(self, drawer,pattern_,scale_=[1.0,1.0], translate_=[0,0],rotation_=0, ink=1,fill=(255,255,255,128)):
        pattern = scale(pattern_, scale_[0], scale_[1], 1.0)
        pattern = rotate(pattern,rotation_)
        pattern = translate(pattern,translate_[0],translate_[1])
        a=pattern.geoms
        for b in a:
            c_ = list(b.coords)
            coords = (c_[0][0],c_[0][1],c_[1][0],c_[1][1])
            drawer.line(coords,fill,ink)
            
    def draw_pattern_a(self, drawer,pattern_,scale_=[1.0,1.0], translate_=[0,0],rotation_=0, ink=1,fill=(255,255,255,128)):
        p = aggdraw.Pen(fill, ink)
    
        pattern = scale(pattern_, scale_[0], scale_[1], 1.0)
        pattern = rotate(pattern,rotation_)
        pattern = translate(pattern,translate_[0],translate_[1])
        a=pattern.geoms
        for b in a:
            c_ = list(b.coords)
            coords = (c_[0][0],c_[0][1],c_[1][0],c_[1][1])
            drawer.line(coords, p)
            
    @property
    def n_params(self):
        return self.n_triangle * 6 # [x0, y0, x1, y1, x2, y2, r, g, b, a]
         
    def random_params(self):
        return np.random.rand(self.n_params)
    
    def render(self, params, background='white', aggdraw_=True, vision=True):
       # print('render')
       
        pattern = MultiLineString(self.pattern)
       
        h, w = self.h, self.w
        alpha_scale = self.alpha_scale
        coordinate_scale = self.coordinate_scale
    
        params = params.reshape(self.n_triangle, 6).copy()
        
        n_triangle = params.shape[0]
        n_feature = params.shape[1]
        for j in range(n_feature):
            params[:, j] = (params[:, j] - params[:, j].min()) / (params[:, j].max() - params[:, j].min())
        
        if background == 'noise':
            img = Image.fromarray(  (np.random.rand( h, w, 3 ) * 255).astype(np.uint8) )
        elif background == 'white':
            img = Image.new("RGBA", (w, h), (128, 128, 128,255))
        elif background == 'black':
            img = Image.new("RGB", (w, h), (0, 0, 0))
        else:
            assert False
            
        if not aggdraw_:
            drawer = ImageDraw.Draw(img)
        else:
            drawer = aggdraw.Draw(img)
        params = params.tolist()
        #print(len(params), "params")
        for i in range(n_triangle):
 
            slice_ = params[i]
            x, y, h_, w_, rotation, alpha = slice_
            
            x *= coordinate_scale
            y *= coordinate_scale
            y *= h
            x *= w
            
            height = int((int(h_*10)/10.0) * h/2)
            width = int((int(w_*10)/10.0) * w/2)
            height += 5
            width += 5
            scale_h = height/40.0
            scale_w = width/40.0
            scale = (scale_w, scale_h)
            rotation = int((int(rotation*6)/6.0) * 180)
            alpha = int((int(alpha*12)/12.0) * 255)
            fill = (alpha,alpha,alpha,140)
            if not aggdraw_:
                self.draw_pattern(drawer,pattern_=pattern, scale_= scale, translate_=[x,y],rotation_=rotation, fill=fill)
            else:
                self.draw_pattern_a(drawer,pattern_=pattern, scale_= scale, translate_=[x,y],rotation_=rotation, fill=fill)
        
        if aggdraw_:
            drawer.flush()   
        del(drawer)
        #print('end render')
        img_arr = np.array(img.convert("RGB"))
        if vision==True:
          img_arr = gaussian_filter(img_arr, 7)
          img_arr = median_filter(img_arr, 5)
          #img_arr = (exposure.equalize_adapthist(img_arr,51)*255).astype(np.uint8)
        return img_arr

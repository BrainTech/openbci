samples=[ 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127 128 129 130 131 132 133 134 135 136 137 138 139 140 141 142 143 144 145 146 147 148 149 150 151 152 153 154 155 156 157 158 159 160 161 162 163 164 165 166 167 168 169 170 171 172 173 174 175 176 177 178 179 180 181 182 183 184 185 186 187 188 189 190 191 192 193 194 195 196 197 198 199; 200 201 202 203 204 205 206 207 208 209 210 211 212 213 214 215 216 217 218 219 220 221 222 223 224 225 226 227 228 229 230 231 232 233 234 235 236 237 238 239 240 241 242 243 244 245 246 247 248 249 250 251 252 253 254 255 256 257 258 259 260 261 262 263 264 265 266 267 268 269 270 271 272 273 274 275 276 277 278 279 280 281 282 283 284 285 286 287 288 289 290 291 292 293 294 295 296 297 298 299; 300 301 302 303 304 305 306 307 308 309 310 311 312 313 314 315 316 317 318 319 320 321 322 323 324 325 326 327 328 329 330 331 332 333 334 335 336 337 338 339 340 341 342 343 344 345 346 347 348 349 350 351 352 353 354 355 356 357 358 359 360 361 362 363 364 365 366 367 368 369 370 371 372 373 374 375 376 377 378 379 380 381 382 383 384 385 386 387 388 389 390 391 392 393 394 395 396 397 398 399];
is=InfoSource();
is.set_param('number_of_channels',num2str(3));
is.set_param('number_of_samples',num2str(100));
is.set_param('sampling_frequency',num2str(2));
is.set_param('channels_names',{'A','B','C'});
is.save_to_file('test_data.obci.info');
md=MemoryDataSource();
md.set_samples(samples);
md.save_to_file('test_data.obci.dat');
tags(1,10)=Tag();
tag_names={'neg','neu','pos','neu','pos','neu','pos','neg','pos','pos'};
tag_position=[1,2,2.5,3.2,5,20,30,30.7,40,50];
for i=1:10
    tags(i).name=tag_names{i};
    tags(i).start_timestamp=tag_position(i);
    tags(i).channelNumber=num2str(i);    
end
ts=TagsSource();
ts.set_tags(tags);
ts.save_to_file('test_data.obci.tags');
rm = ReadManager('test_data.obci.info','test_data.obci.dat','test_data.obci.tags');


se1=SmartTagEndTagDefinition({'neg'},'pos',-1,2);
se2=SmartTagEndTagDefinition({'pos'},'neg',-2,1);

sd1=SmartTagDurationDefinition(4,'neg',-1,20);
sd2=SmartTagDurationDefinition(10,'pos',-3,10);

smgr1=SmartTagsManager(se1,'test_data.obci.info','test_data.obci.dat','test_data.obci.tags');
smgr2=SmartTagsManager([se1,se2],'test_data.obci.info','test_data.obci.dat','test_data.obci.tags');
smgr3=SmartTagsManager(sd1,'test_data.obci.info','test_data.obci.dat','test_data.obci.tags');
smgr4=SmartTagsManager(sd2,'test_data.obci.info','test_data.obci.dat','test_data.obci.tags');

tags1=smgr1.get_smart_tags;
%end_tags1=[tags1.end_tag];
%start_tags1=[tags1.start_tag];



tags2=smgr2.get_smart_tags;
tags3=smgr3.get_smart_tags;
tags4=smgr4.get_smart_tags;

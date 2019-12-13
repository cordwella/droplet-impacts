

prompt = {'Magnet to stage length (mm):','Stage Width (mm):'};
dlgtitle = 'Input';
dims = [1 35];
definput = {'10','7.5'};
answer = inputdlg(prompt,dlgtitle,dims,definput)

length = str2num(answer{1});
width = str2num(answer{2});

total_length = length + width

field = Interpolate_field(total_length);

fprintf("Total Distance %f mm \nField Strength = %f T \n", total_length, field);

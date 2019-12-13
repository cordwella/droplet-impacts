% code originally from the server, I don't know who the orignial author is
function [interp_values]=Interpolate_field(heights)

list = {'25mm Strong Magnet','30mm Thin Magnet','15mm Old Magnet','Other'};
[indx,tf] = listdlg('ListString',list);
if tf == 1
    if indx == 1
        FileName = '25mm.csv';
    end
    if indx == 2
        FileName = '30mm.csv';
    end
    if indx == 3
        FileName = '15mm.csv';
    end
    if indx == 4
    [FileName,PathName] = uigetfile('*.csv','Select the calibration data'); % asks the user to select the CSV file with calibration data
    end

B=csvread(FileName,2,0); %read field data from 2nd line. Field above the magent's centre is in column 4 (gauss). Column 1 gives position in mm.
interp_values=interp1(B(:,1),B(:,7),heights,'spline',0)/1e4; %interpolate B field at given distance from magnet (tesla)
end
end
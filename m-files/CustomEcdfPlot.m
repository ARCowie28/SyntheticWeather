
% � All rights reserved. 
% ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, 
% Interdisciplinary Laboratory of Performance-Integrate Design, 2016
% Parag Rastogi
% See the LICENSE.TXT file for more details.

function CustomEcdfPlot(plotser,plotf,filepath,varargin)

% % This function brings together the code needed to plot the descriptive
% % plots used in the CreateSyntheticFiles script

p = inputParser;
p.FunctionName = 'CustomEcdfPlot';

addRequired(p,'plotser',@isstruct)
addRequired(p,'plotf',@ischar)
addRequired(p,'filepath',@(x) (ischar(x) | iscell(x)))
addParameter(p,'xlabelCustom','',@(x) (ischar(x) | iscell(x)))
addParameter(p,'titleCustom','',@(x) (ischar(x) | iscell(x)))
addParameter(p,'visible','on',@ischar)
addParameter(p,'plotCI',false,@islogical)
addParameter(p,'CCdata',false,@islogical)

parse(p, plotser, plotf, filepath, varargin{:})

plotser = p.Results.plotser;

if iscell(p.Results.filepath)
	filepath = p.Results.filepath{1};
else
	filepath = p.Results.filepath;
end

if iscell(p.Results.xlabelCustom)
	xlabelCustom = p.Results.xlabelCustom{1};
else
	xlabelCustom = p.Results.xlabelCustom;
end

if iscell(p.Results.titleCustom)
	titleCustom = p.Results.titleCustom{1};
else
	titleCustom = p.Results.titleCustom;
end

visible = p.Results.visible;
CCdata = p.Results.CCdata;
% Plot Confidence Intervals or NOT
plotCI = p.Results.plotCI;
% Convert the incoming plotf string to uppercase
plotf = p.Results.plotf;


DefaultColours
% set(0, 'defaultAxesFontName', 'Helvetica')
set(0, 'defaultAxesUnits', 'normalized')

PlotHandle = figure('visible',visible);

% Get current axes, and turn on HOLD
ax = gca; hold(ax, 'on'); ax.Box = 'on';

if CCdata
	for k = 1:size(plotser.rcp45.(plotf).x,1)
	% Climate change data
	H2(k) = plot(plotser.rcp45.(plotf).x(k,2:end), ...
		plotser.rcp45.(plotf).e(k,:));
	H3(k) = plot(plotser.rcp85.(plotf).x(k,2:end), ...
		plotser.rcp85.(plotf).e(k,:));
		
	H2(k).LineStyle = '-';
	H2(k).LineWidth = 1;
	H2(k).Color = orange;
	H3(k).LineStyle = '-';
	H3(k).LineWidth = 1;
	H3(k).Color = red;
	end
	
	% For the spellcdf plots, increase line width
	if k == 1
		H2(k).LineWidth = 3;
		H3(k).LineWidth = 3;
	end
else
	% Synthetic data
	for k = 1:size(plotser.syn.(plotf).x,1)
	H2(k) = plot(plotser.syn.(plotf).x(k,2:end), ...
		plotser.syn.(plotf).e(k,:));
	H2(k).LineStyle = '-';
	H2(k).LineWidth = 1;
	H2(k).Color = orange;
	end
	
	% For the spellcdf plots, increase line width
	if k == 1
		H2(k).LineWidth = 2;
	end
end


% Recorded data
if isfield(plotser,'rec')
	H1 = plot(plotser.rec.(plotf).x(2:end),plotser.rec.(plotf).e);	
	H1.LineStyle = '-';
	H1.LineWidth = 3;
	H1.Color = blue;	
end

if isfield(plotser,'tmy')
	% TMY data
	H4 = plot(plotser.tmy.(plotf).x(2:end),plotser.tmy.(plotf).e);
	H4.Color = grey;
	H4.LineWidth = 3;
	H4.LineStyle = ':';
end

if plotCI
	H5(1) = plot(plotser.rec.(plotf).x(2:end), ...
		plotser.rec.(plotf).flo);
	H5(2) = plot(plotser.rec.(plotf).x(2:end), ...
		plotser.rec.(plotf).fup);
end

hold(ax, 'off');

ax.YLim = [0,1];
ax.FontSize = 20;
ax.LabelFontSizeMultiplier = 1.125;
ax.TitleFontSizeMultiplier = 1.125;

if isfield(plotser,'rec')
	LegendCell = {'Recorded'};
	LegendVec = H1;
else
	LegendCell = {};
	LegendVec = [];
end

if ~CCdata
	if isfield(plotser,'tmy')
		LegendCell = [LegendCell, {'Synthetic','TMY'}];
		LegendVec = [LegendVec, H2(1), H4];
	else
		LegendCell = [LegendCell, {'Synthetic'}];
		LegendVec = [LegendVec, H2(1)];
	end
	
else
	if isfield(plotser,'tmy')
		LegendCell = [LegendCell, {'RCP4.5','RCP8.5','TMY'}];
		LegendVec = [LegendVec, H2(1), H3(1), H4];
	else
		LegendCell = [LegendCell, {'RCP4.5','RCP8.5'}];
		LegendVec = [LegendVec, H2(1), H3(1)];
	end
end

leg = legend(ax,LegendVec, LegendCell, 'Location', 'southeast');
leg.FontSize = ax.FontSize;

if plotCI
	H5(1).Color = lgrey;
	H5(2).Color = lgrey;
	H5(1).LineWidth = 2;
	H5(2).LineWidth = 2;
end

ax.YLabel.String = 'CDF';

if isempty(xlabelCustom)
	if strcmpi(plotf,'TDB')
		ax.XLabel.String = 'Temperature [K]';
	elseif strcmpi(plotf,'GHI')
		ax.XLabel.String = 'Solar Radiation [W/m^2]';
	elseif strcmpi(plotf,'W')
		ax.XLabel.String = 'Humidity Ratio [unitless]';
	elseif strcmpi(plotf,'RH')
		ax.XLabel.String = 'Relative Humidity [%]';
	end
else
	ax.XLabel.String = xlabelCustom;
end

ax.Title.String = titleCustom;

SaveThatFig(PlotHandle, filepath)


% Re-colour in Grey and Save again
if isfield(plotser,'rec')
	H1.Color = grey;
end

for k = 1:length(H2)
	H2(k).Color = grey;
end

if CCdata
	% RCP8.5, if it exists. RCP 4.5 takes the properties of
	% the SYN series.
	for k = 1:length(H3)
		H3(k).Color = grey;
		H3(k).LineStyle = '-.';
	end
end

if isfield(plotser,'tmy')
	H4.Color = grey;
end

if plotCI
	H5(1).Color = rgb2gray(H5(1).Color);
	H5(2).Color = rgb2gray(H5(2).Color);
end

SaveThatFig(PlotHandle, [filepath,'-BW'], 'printfig', false)

end
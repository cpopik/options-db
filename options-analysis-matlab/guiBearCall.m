function varargout = guiBearCall(varargin)
% GUIBEARCALL MATLAB code for guiBearCall.fig
%      GUIBEARCALL, by itself, creates a new GUIBEARCALL or raises the existing
%      singleton*.
%
%      H = GUIBEARCALL returns the handle to a new GUIBEARCALL or the handle to
%      the existing singleton*.
%
%      GUIBEARCALL('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in GUIBEARCALL.M with the given input arguments.
%
%      GUIBEARCALL('Property','Value',...) creates a new GUIBEARCALL or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before guiBearCall_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to guiBearCall_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help guiBearCall

% Last Modified by GUIDE v2.5 22-Jan-2016 21:47:16

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @guiBearCall_OpeningFcn, ...
                   'gui_OutputFcn',  @guiBearCall_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT
end

% --- Executes just before guiBearCall is made visible.
function guiBearCall_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to guiBearCall (see VARARGIN)

% Choose default command line output for guiBearCall
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes guiBearCall wait for user response (see UIRESUME)
% uiwait(handles.figure1);
end

% --- Outputs from this function are returned to the command line.
function varargout = guiBearCall_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;
end


function tickerBox_Callback(hObject, eventdata, handles)
% hObject    handle to tickerBox (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tickerBox as text
%        str2double(get(hObject,'String')) returns contents of tickerBox as a double
end

% --- Executes during object creation, after setting all properties.
function tickerBox_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tickerBox (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
end

% --- Executes on button press in runButton.
function runButton_Callback(hObject, eventdata, handles)
% hObject    handle to runButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    ticker = get(handles.tickerBox, 'string');
    type = 'CALL';
    var = 'bsVol';
    date = today;

    % ESTABLISH DATABASE CONNECTION
    conn = database('options','admin','servire87','Vendor','MySQL','Server','www.derivs.xyz');
    query = ['SELECT expiry, strike, bid, ask, underlying, bsDelta, bsGamma, bsTheta, bsVega, contract FROM options.$' ticker ' WHERE type = ''' type ''' AND bsVol != 0 AND date = ' num2str(date) ';'];

    % RETURN THE DATA FROM THE DATABASE
    curs = exec(conn, query);
    curs = fetch(curs);
    d = cell2mat(curs.Data(:,1:9));
    c = curs.Data(:,10);

    % REDEFINE DATES TO DAYS
    d(:,1) = d(:,1) - today;
    c = c(abs(d(:,1)-30) < 4, :);
    d = d(abs(d(:,1)-30) < 4, :);
    c = c(d(:,2) > d(:,5), :);
    d = d(d(:,2) > d(:,5), :);
    c = c(d(:,3) ~= 0, :);
    d = d(d(:,3) ~= 0, :);

    % INITIALIZING DATA
    expVal = 0;
    maxLoss = 0;
    maxProfit = 0;
    delta = 0;
    gamma = 0;
    theta = 0;
    vega = 0;
    
    for i = 1:length(d(:,1))
        for j = i:length(d(:,1))
            expVal(i,j) = expVal_bearCallSpread(d(i,2), d(j,2), d(i,3), d(j,4), d(1,5), .08, d(1,1));
            maxLoss(i,j) = -(d(i,2)-d(j,2));
            maxProfit(i,j) = d(i,3)-d(j,4);
            delta(i,j) = -d(i,6) + d(j,6);
            gamma(i,j) = -d(i,7) + d(j,7);
            theta(i,j) = -d(i,8) + d(j,8);
            vega(i,j) = -d(i,9) + d(j,9);
        end
    end

    % DISPLAY DATA
    set(handles.dataTable, 'Data', expVal)
    set(handles.dataTable, 'ColumnName', d(:, 2))
    set(handles.dataTable, 'RowName', d(:, 2))
    set(handles.dataTable, 'ColumnWidth', {60})
    
    setappdata(guiBearCall,'contract',c);
    setappdata(guiBearCall,'rawData',d);
    setappdata(guiBearCall,'expVal',expVal);
    setappdata(guiBearCall,'maxProfit',maxProfit);
    setappdata(guiBearCall,'maxLoss',maxLoss);
    setappdata(guiBearCall,'delta',delta);
    setappdata(guiBearCall,'gamma',gamma);
    setappdata(guiBearCall,'theta',theta);
    setappdata(guiBearCall,'vega',vega);

end


% --- Executes when selected cell(s) is changed in dataTable.
function dataTable_CellSelectionCallback(hObject, eventdata, handles)
% hObject    handle to dataTable (see GCBO)
% eventdata  structure with the following fields (see MATLAB.UI.CONTROL.TABLE)
%	Indices: row and column indices of the cell(s) currently selecteds
% handles    structure with handles and user data (see GUIDATA)

    indices = eventdata.Indices(1,:);
    i = indices(1); j = indices(2);
    
    % INFO TABLE
    cont = getappdata(guiBearCall,'contract');
    raw = getappdata(guiBearCall,'rawData');
    infoData = {'Contract' cont{i,1} cont{j,1}; 'Strike' raw(i,2) raw(j,2); 'Expiry Date' datestr(raw(i,1) + today,'mm-dd-YY') datestr(raw(j,1) + today,'mm-dd-yy'); ...
                'Days ''til Expiry' raw(i,1) raw(j,1)};
    set(handles.infoTable, 'data', infoData);
    
    % METRIC TABLE
    maxProfit = getappdata(guiBearCall,'maxProfit')*100;
    maxLoss = getappdata(guiBearCall,'maxLoss')*100;
    expVal = getappdata(guiBearCall,'expVal');
    metricData = {'Max Profit' maxProfit(i,j); 'Max Loss' maxLoss(i,j); 'B/E Vol' ''; 'Exp. Value' expVal(i,j)};
    set(handles.metricTable, 'data', metricData);
    
    % GREEK TABLE
    delta = getappdata(guiBearCall,'delta');
    gamma = getappdata(guiBearCall,'gamma');
    theta = getappdata(guiBearCall,'theta');
    vega = getappdata(guiBearCall,'vega');
    greekData = {'Delta' delta(i,j); 'Gamma' gamma(i,j); 'Theta' theta(i,j); 'Vega' vega(i,j)};
    set(handles.greekTable, 'data', greekData);
    
end


% --- Executes on key press with focus on tickerBox and none of its controls.
function tickerBox_KeyPressFcn(hObject, eventdata, handles)
% hObject    handle to tickerBox (see GCBO)
% eventdata  structure with the following fields (see MATLAB.UI.CONTROL.UICONTROL)
%	Key: name of the key that was pressed, in lower case
%	Character: character interpretation of the key(s) that was pressed
%	Modifier: name(s) of the modifier key(s) (i.e., control, shift) pressed
% handles    structure with handles and user data (see GUIDATA)
    if isequal(eventdata.Character,char(13))
        runButton_Callback(hObject, eventdata, handles);
    end

end


% Download options across all expiries and skew for a specific ticker from Google Finance

function DataOut = getOptionsData_GOOGLE(symbolid)
%
% DataOut = getGoogleOptionsData(symbol)
% Inputs: Stock ticker as string (e.g., 'INTC')
% Output:  A array of cells containing the following structure for each
% contract
%          ticker: String of the stock ticker
%      optionType: String 'CALL' or 'PUT' indicating the option type
%             cid: String of the CID
%            name: String of the name (usually empty)
%               s: String of the "s" element in the Google json file
%               e: String of the "e" element in the Google json file
%           price: Numeric price of the option; NaN if no data
%          change: Numeric price of the change in price; NaN if no data
%             bid: Numeric bid price; NaN if no data
%             ask: Numeric ask price; NaN if no data
%    openInterest: Numeric open interest; NaN if no data
%          volume: Numeric volume; NaN if no data (usually)
%          strike: Numeric strike price; NaN if no data
%       expiryStr: String of the expiration date (Format: 'Dec 20, 2014')
%          expiry: Numeric of the expieration date (Matlab convention)
%
%   Returns {} if no data.
%
% Examples:
%           DataOut = getGoogleOptionsData('INTC');
%           disp(' ');
%           disp('List the first contract in the array');
%           DataOut{1} 
%
%           disp(' ');
%           disp('Display the first contract''s expiry');
%           datedisp(DataOut{1}.expiry) 
%
%           disp(' ');
%           disp('To show only PUT options with expiry 30 days away');
%           disp('and open interest of at least 10000');
%           daysAway = 30;
%           minOpenInt = 10000;
%           optionType = 'PUT';
%           ind = find(...
%             arrayfun(@(i) DataOut{i}.expiry-today(),1:numel(DataOut)) ...
%               >=daysAway & ...
%             arrayfun(@(i) DataOut{i}.openInterest,1:numel(DataOut)) ...
%               >=minOpenInt & ...
%             strcmp(arrayfun(@(i) DataOut{i}.optionType,1:numel(DataOut), ...
%              'UniformOutput',false),optionType));
%           strike = arrayfun(@(i) DataOut{i}.strike,ind) ;
%           expiry = arrayfun(@(i) DataOut{i}.expiry,ind);
%           openInt = arrayfun(@(i) DataOut{i}.openInterest,ind);
%           datedisp([expiry' strike' openInt']);
%
% (c) C Lau via econdataresearch.blogspot.com; version: 1.1
%

% Version:
% 1.1  I added some try/catches so the function will handle errors more gracefully 
% if used within other matlab code. If urlread returns an error,
% the function now returns an empty cell array {};
%   I also added an example of selecting and display options with certain criteria
%

% History: I referenced the code for Get_Yahoo_Options_Data from
% tradingwithmatlab.blogspot.com, which I used to retrieve options data
% from Yahoo before the code stopped working. Thus the variable names are 
% similar.
% I originally wanted to replicate Get_Yahoo_Options_Data's output exactly, 
% but I can't quite remember the exact output and didn't want to spend the
% time to figure it out from the code. Thus, the output also differs
% from Get_Yahoo_Options_Data. Unfortunately, this means you cannot just 
% plug this function into Get_Yahoo_Options_Data's place and have it work. 
%
% Other notes: 
% a) I replaced all the "-" in the json data with NaN.
% b) There are sometimes data for the p and c elements (price and changes)
% that are ignored. I am not sure what they are.
% c) The code parses and returns all the contracts in the Google json file.
% Do note that a lot of the contracts have no data.


debug = 0;

if debug==1
    symbolid = 'ED';
end

if nargin < 1
    disp('Please type "help getGoogleOptionsData" for syntax.');
    return;
end

try
    urlExpiry = urlread(['http://www.google.com/finance/option_chain?q=' symbolid '&output=json']);
catch ME
    disp(ME);
    sprintf('Error: Cannot retrieve option data using urlread for %s\n',symbolid);
    DataOut = {};
    return;
end
    
% E.g. of data: 
  % expirations:[
  %    {y:2014,m:12,d:5},{y:2014,m:12,d:12},{y:2014,m:12,d:20},{y:2014,m:12,d:26},{y:2015,m:1,d:2},{y:2015,m:1,d:9},{y:2015,m:1,d:17},{y:2015,m:2,d:20},{y:2015,m:3,d:20},{y:2015,m:4,d:17},{y:2015,m:7,d:17},{y:2016,m:1,d:15},{y:2017,m:1,d:20}
  %    ]
tt = regexp(urlExpiry,'expirations:\[(.*)\],puts','tokens');
if isempty(tt)
   DataOut = {};
   return; 
end
expiry = regexp(tt{1}{1},'{y:(?<yy>\d+),m:(?<mm>\d+),d:(?<dd>\d+)}','names');


for tempi = 1:size(expiry,2)

    
    try
        urlContract = urlread(['http://www.google.com/finance/option_chain?q=' symbolid '&output=json&expy=' expiry(tempi).yy '&expm=' expiry(tempi).mm '&expd=' expiry(tempi).dd]);
    catch ME
        disp(ME);
        sprintf('Error: Cannot retrieve option expiry data using urlread for %s\n',symbolid);
        continue;
    end

    
    tt = regexp(urlContract,'puts:\[(.*)\],calls','tokens');
        % Note the ",calls" to capture only the call data
    putsTT{tempi} = regexp(tt{1}{1},'{cid:"(?<cid>.*?)",name:"(?<name>.*?)",s:"(?<s>.*?)",e:"(?<e>.*?)",p:"(?<p>.*?)",c:"(?<c>.*?)",b:"(?<b>.*?)",a:"(?<a>.*?)",oi:"(?<oi>.*?)",vol:"(?<vol>.*?)",strike:"(?<strike>.*?)",expiry:"(?<expiry>.*?)"}','names');
		% E.g. of put data: 
        % {cid:"545233775057295",name:"",s:"INTC141205P00024000",e:"OPRA",p:"-",c:"-",b:"-",a:"0.02",oi:"0",vol:"-",strike:"24.00",expiry:"Dec 5, 2014"}
        % {cid:"92955275286566",name:"",s:"INTC141205P00025000",e:"OPRA",p:"-",c:"-",b:"-",a:"0.02",oi:"0",vol:"-",strike:"25.00",expiry:"Dec 5, 2014"}

    tt = regexp(urlContract,'calls:\[(.*)\],underlying','tokens');
        % Note the ",underlying" to capture only the call data
    callsTT{tempi} = regexp(tt{1}{1},'{cid:"(?<cid>.*?)",name:"(?<name>.*?)",s:"(?<s>.*?)",e:"(?<e>.*?)",p:"(?<p>.*?)",c:"(?<c>.*?)",b:"(?<b>.*?)",a:"(?<a>.*?)",oi:"(?<oi>.*?)",vol:"(?<vol>.*?)",strike:"(?<strike>.*?)",expiry:"(?<expiry>.*?)"}','names');
        % E.g. of call data: 
        % {cid:"259510024302043",name:"",s:"INTC141205C00024000",e:"OPRA",p:"-",c:"-",b:"11.75",a:"13.50",oi:"0",vol:"-",strike:"24.00",expiry:"Dec 5, 2014"},
        % {cid:"141592700369825",name:"",s:"INTC141205C00025000",e:"OPRA",p:"-",c:"-",b:"10.75",a:"12.50",oi:"0",vol:"-",strike:"25.00",expiry:"Dec 5, 2014"},
end

clear DataOut;
dataOutCounter = 0;
for tempi = 1:size(expiry,2)
    % For some reason, google data has extra stuff in the "p" and "c"
    % elements. Example: 
    %       p: '2.35",cs:"chr'
    %       c: '-0.33",cp:"-12.31'
    
    for tempj = 1:size(callsTT{tempi},2)
        dataOutCounter = dataOutCounter+1;
    
        DataOut{dataOutCounter}.ticker = symbolid;
        DataOut{dataOutCounter}.optionType = 'CALL';

        DataOut{dataOutCounter}.cid = callsTT{tempi}(tempj).cid;
        DataOut{dataOutCounter}.name = callsTT{tempi}(tempj).name;
        DataOut{dataOutCounter}.s = callsTT{tempi}(tempj).s;
        DataOut{dataOutCounter}.e = callsTT{tempi}(tempj).e;
        tt = regexp(callsTT{tempi}(tempj).p,'([-\.\d]+)"','tokens');
        if isempty(tt)
            DataOut{dataOutCounter}.price = callsTT{tempi}(tempj).p;
        else
            DataOut{dataOutCounter}.price = tt{1}{1};
        end
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.price,'-')
            DataOut{dataOutCounter}.price = nan;
        else
            DataOut{dataOutCounter}.price = str2num(strrep(DataOut{dataOutCounter}.price,',',''));
        end
        
        tt = regexp(callsTT{tempi}(tempj).c,'([-\.\d]+)"','tokens');
        if isempty(tt)
            DataOut{dataOutCounter}.change = callsTT{tempi}(tempj).c;
        else
            DataOut{dataOutCounter}.change = tt{1}{1};
        end
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.change,'-')
            DataOut{dataOutCounter}.change = nan;
        else
            DataOut{dataOutCounter}.change = str2num(strrep(DataOut{dataOutCounter}.change,',',''));
        end
        DataOut{dataOutCounter}.bid = callsTT{tempi}(tempj).b;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.bid,'-')
            DataOut{dataOutCounter}.bid = nan;
        else
            DataOut{dataOutCounter}.bid = str2num(strrep(DataOut{dataOutCounter}.bid,',',''));
        end
        
        DataOut{dataOutCounter}.ask = callsTT{tempi}(tempj).a;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.ask,'-')
            DataOut{dataOutCounter}.ask = nan;
        else
            DataOut{dataOutCounter}.ask = str2num(strrep(DataOut{dataOutCounter}.ask,',',''));
        end
        
        DataOut{dataOutCounter}.openInterest = callsTT{tempi}(tempj).oi;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.openInterest,'-')
            DataOut{dataOutCounter}.openInterest = nan;
        else
            DataOut{dataOutCounter}.openInterest = str2num(strrep(DataOut{dataOutCounter}.openInterest,',',''));
        end
        
        DataOut{dataOutCounter}.volume = callsTT{tempi}(tempj).vol;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.volume,'-')
            DataOut{dataOutCounter}.volume = nan;
        else
            DataOut{dataOutCounter}.volume = str2num(strrep(DataOut{dataOutCounter}.volume,',',''));
        end
        
        DataOut{dataOutCounter}.strike = callsTT{tempi}(tempj).strike;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.strike,'-')
            DataOut{dataOutCounter}.strike = nan;
        else
            DataOut{dataOutCounter}.strike = str2num(strrep(DataOut{dataOutCounter}.strike,',',''));
        end
        
        DataOut{dataOutCounter}.expiryStr = callsTT{tempi}(tempj).expiry;
        DataOut{dataOutCounter}.expiry = datenum(callsTT{tempi}(tempj).expiry);
          % use matlab dates
    end
    
    
    for tempj = 1:size(putsTT{tempi},2)
        dataOutCounter = dataOutCounter+1;
    
        DataOut{dataOutCounter}.ticker = symbolid;
        DataOut{dataOutCounter}.optionType = 'PUT';
  
        DataOut{dataOutCounter}.cid = putsTT{tempi}(tempj).cid;
        DataOut{dataOutCounter}.name = putsTT{tempi}(tempj).name;
        DataOut{dataOutCounter}.s = putsTT{tempi}(tempj).s;
        DataOut{dataOutCounter}.e = putsTT{tempi}(tempj).e;
        tt = regexp(putsTT{tempi}(tempj).p,'([-\.\d]+)"','tokens');
        if isempty(tt)
            DataOut{dataOutCounter}.price = putsTT{tempi}(tempj).p;
        else
            DataOut{dataOutCounter}.price = tt{1}{1};
        end
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.price,'-')
            DataOut{dataOutCounter}.price = nan;
        else
            DataOut{dataOutCounter}.price = str2num(strrep(DataOut{dataOutCounter}.price,',',''));
        end
        
        tt = regexp(putsTT{tempi}(tempj).c,'([-\.\d]+)"','tokens');
        if isempty(tt)
            DataOut{dataOutCounter}.change = putsTT{tempi}(tempj).c;
        else
            DataOut{dataOutCounter}.change = tt{1}{1};
        end
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.change,'-')
            DataOut{dataOutCounter}.change = nan;
        else
            DataOut{dataOutCounter}.change = str2num(strrep(DataOut{dataOutCounter}.change,',',''));
        end
        DataOut{dataOutCounter}.bid = putsTT{tempi}(tempj).b;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.bid,'-')
            DataOut{dataOutCounter}.bid = nan;
        else
            DataOut{dataOutCounter}.bid = str2num(strrep(DataOut{dataOutCounter}.bid,',',''));
        end
        
        DataOut{dataOutCounter}.ask = putsTT{tempi}(tempj).a;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.ask,'-')
            DataOut{dataOutCounter}.ask = nan;
        else
            DataOut{dataOutCounter}.ask = str2num(strrep(DataOut{dataOutCounter}.ask,',',''));
        end
        
        DataOut{dataOutCounter}.openInterest = putsTT{tempi}(tempj).oi;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.openInterest,'-')
            DataOut{dataOutCounter}.openInterest = nan;
        else
            DataOut{dataOutCounter}.openInterest = str2num(strrep(DataOut{dataOutCounter}.openInterest,',',''));
        end
        
        DataOut{dataOutCounter}.volume = putsTT{tempi}(tempj).vol;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.volume,'-')
            DataOut{dataOutCounter}.volume = nan;
        else
            DataOut{dataOutCounter}.volume = str2num(strrep(DataOut{dataOutCounter}.volume,',',''));
        end
        
        DataOut{dataOutCounter}.strike = putsTT{tempi}(tempj).strike;
        % more data cleanup
        if strcmp(DataOut{dataOutCounter}.strike,'-')
            DataOut{dataOutCounter}.strike = nan;
        else
            DataOut{dataOutCounter}.strike = str2num(strrep(DataOut{dataOutCounter}.strike,',',''));
        end
        
        DataOut{dataOutCounter}.expiryStr = putsTT{tempi}(tempj).expiry;
        DataOut{dataOutCounter}.expiry = datenum(putsTT{tempi}(tempj).expiry);
        % use matlab dates
    end
    
end
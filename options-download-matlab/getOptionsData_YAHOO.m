% Download options across all expiries and skew for a specific ticker from Yahoo Finance

function dataOut = getOptionsData_YAHOO( ticker, ExpDate)

if nargin < 2
    error('input function has one agument, it require minimum two inputs')
    return;
end

if nargin < 3
    typeOutData=[];
end

% yahoo finance url and html code
dateUnix = int32(floor(86400 * (datenum(ExpDate) - datenum('01-Jan-1970'))));
disp(sprintf(['\tdownloading: http://finance.yahoo.com/q/op?s=' ticker '+Options' '&date=' num2str(dateUnix)]))
html = urlread(['http://finance.yahoo.com/q/op?s=' ticker '+Options' '&date=' num2str(dateUnix)]);

Strike = regexpi(html, ['/q/op.s=' ticker '&strike=([^"]*)'], 'tokens'); % Strike

if (~isempty(Strike))

    ContractName = regexpi(html, ['/q.s=' ticker '([^"]*)'], 'tokens'); % ContractName
    OptionPriceAdd = regexp(html, '<div class="option_entry Fz-m" >([^"]*[^%])</div>', 'tokens'); %lastPrice, Bid, Ask, change, Volume, openInterest, impliedVolatiliti
    impliedVolatility = regexp(html, '<div class="option_entry Fz-m" >([^"]*[^%])%</div>', 'tokens'); %lastPrice, Bid, Ask, change, Volume, openInterest, impliedVolatiliti
    Volume = regexpi(html, ' <strong data-sq=":volume" data-raw="(\d*)">([^"]*)</strong>', 'tokens'); % Volume

    % FIX COMMAS IN STRIKE
    for i = 1:length(Strike)
        Strike{i} = strrep(Strike{i},',','');
    end
    Strike = CellStr2Num(Strike);
    OptionPriceAdd = CellStr2Num(OptionPriceAdd);
    impliedVolatility = CellStr2Num(impliedVolatility);
    Volume = CellStr2Num(Volume(1:2:end));
    OptType = getType(ContractName, ticker);
    ContractName=ContractName(2:end-1);
    lastPrice = OptionPriceAdd([1:5:end]);
    Bid = OptionPriceAdd([2:5:end]);
    Ask = OptionPriceAdd([3:5:end]);
    change = OptionPriceAdd([4:5:end]);
    openInterest = OptionPriceAdd([5:5:end]);
    
    for i = 1:length(Strike)
        dataOut{i}.ticker = ticker;
        dataOut{i}.expStr = ExpDate;
        dataOut{i}.optionType = OptType{i};
        dataOut{i}.strike = Strike(i);
        dataOut{i}.s = strcat(ticker,ContractName{i}{1});
        dataOut{i}.price = lastPrice(i);
        dataOut{i}.bid = Bid(i);
        dataOut{i}.ask = Ask(i);
        dataOut{i}.change = change(i);
        dataOut{i}.volume = Volume(i);
        dataOut{i}.cid = 0;
        dataOut{i}.name = 'NULL';
        dataOut{i}.e = 'NULL';
        dataOut{i}.expiry = datenum(ExpDate);
        dataOut{i}.openInterest = openInterest(i);
    end
else
    dataOut = {};
end

end

function [ output ] = CellStr2Num( imput )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

cells = cellfun(@(x)str2num(sprintf('%s ', x{:})), imput, 'Uniform', false);
output = cell2mat(cells)';

end

function output = getType(input, ticker)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

for i=2:(length(input)-1)
    a = input(i);
    b = char(a{1});
    flag = b(7);
    if (flag == 'P')
        output{i-1} = 'PUT';
    else
        output{i-1} = 'CALL';
    end
end

end


% Download options across all expiries and skew for a specific ticker 

function optionsData = getOptionsData(ticker, useYahoo)
    % GET RISK FREE CURVE (TREASURY)
    [zeroDates, zeroRates] = getYieldCurve();

    if (useYahoo == 0)
        optionsData = getOptionsData_GOOGLE(ticker);
    else
        % DEFINING DATES
        dayNumber = weekday(today);
        startDay = today + (6-dayNumber);
        startDay = int32(floor(86400 * (datenum(startDay) - datenum('01-Jan-1970'))));  % change to unix
        
        html = urlread(['http://finance.yahoo.com/q/op?s=' ticker '&date=' num2str(startDay)]);

        dates1 = regexpi(html, ['/q/op\?s=' ticker '&date=([^"]*)'], 'tokens'); % Strike
        cells = cellfun(@(x)str2num(sprintf('%s ', x{:})), dates1, 'Uniform', false);
        dates = cell2mat(cells)';
        % RETURN TO MATLAB TIME
        dates = dates/86400 + datenum(1970,1,1);
        checkDates = mod(dates - dates(1),7);  % fixing weird yahoo thing
        dates = dates(checkDates == 0);

        % GETTING THE FORWARD EXPIRIES
        strDates = cellstr(datestr(dates, 'yyyy-mm-dd'));

        % CONCATENATING CELL ARRAYS
        optionsData = getOptionsData_YAHOO(ticker, strDates(1));
        for i = 2:length(strDates)
            add = getOptionsData_YAHOO(ticker, strDates(i));
            if (~isempty(add))
                optionsData = cat(2 , optionsData, add);
            end
        end
    end    

    % PRICE AND DIVIDEND YIELD INFORMATION
    c = yahoo;
    stock = fetch(c, ticker);
    divData = fetch(c, ticker, today-360, today, 'v');
    if (~isempty(divData))
       yield = (ones(1,length(divData(:,2))) * divData(:,2))/stock.Last;
    else
       yield = 0; 
    end
    c.close()

    for i = 1:length(optionsData)
        % SET THE CURRENT OPTION
        option = optionsData{i};

        time = daysdif(today, option.expiry, 1)/360;
        [m, index] = min(abs(zeroDates-option.expiry));
        rate = zeroRates(index);

        % BOOL OPTION TYPE
        if (option.optionType(1) == 'C') typeI = 1;
        else typeI = 2; end

        % blsimpv(Price, Strike, Rate, Time, Value, Limit, Yield, Tolerance, Class)
        bsVol = blsimpv(stock.Last, option.strike, rate, time, (option.ask+option.bid)/2, 10, yield, 10^(-4), {lower(option.optionType)});
        
        if (isnan(bsVol))
            option.underlying = stock.Last;
            option.bsVol = 0;
            option.bsDelta = 0;
            option.bsGamma = 0;
            option.bsTheta = 0;
            option.bsVega = 0;
        else
            [deltaCall, deltaPut] = blsdelta(stock.Last, option.strike, rate, time, bsVol, yield); delta = [deltaCall deltaPut];
            bsGamma = blsgamma(stock.Last, option.strike, rate, time, bsVol, yield);
            [thetaCall, thetaPut] = blstheta(stock.Last, option.strike, rate, time, bsVol, yield); theta = [thetaCall/252 thetaPut/252];
            bsVega = blsvega(stock.Last, option.strike, rate, time, bsVol, yield);

            option.underlying = stock.Last;
            option.bsVol = bsVol;
            option.bsDelta = delta(typeI);
            option.bsGamma = bsGamma;
            option.bsTheta = theta(typeI);
            option.bsVega = bsVega;
        end

        % UPDATING THE CELL ARRAY
        optionsData{i} = option;
    end
    
end








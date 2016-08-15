% Upload options to a sql database

function uploadOptions(force)
    % SUPPRESS WARNINGS
    warning('off','all')

    % ONLY DO ON TRADING DAY
    if (nargin == 0); weekdays = [2 3 4 5 6]; end
    if (nargin > 0); weekdays = [1 2 3 4 5 6 7]; end
    
    if (ismember(weekday(today), weekdays) && ~ismember(today, holidays(today,today+1)))

        % ESTABLISH DATABASE CONNECTION
        javaaddpath('/usr/local/MATLAB/R2015b/mysql-connector-java-5.1.38/mysql-connector-java-5.1.38-bin.jar')
        conn = database('options','admin','servire87','Vendor','MySQL','Server','www.derivs.xyz');

        % GET TABLE NAMES
        queryTable = 'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = ''BASE TABLE'' AND TABLE_SCHEMA=''options''';
        curs = exec(conn, queryTable);
        curs = fetch(curs);
        tableNames = curs.Data;
        tableNamesBool = zeros(1,length(tableNames));

        colNames = {'date', 'ticker', 'underlying', 'contract', 'type', 'strike', 'expiry', ...
                    'last', 'bid', 'ask', 'volume', 'openInterest', ...
                    'bsVol', 'bsDelta', 'bsGamma', 'bsTheta', 'bsVega'};
        while (sum(tableNamesBool) ~= length(tableNames))
            for k=1:length(tableNames)
                % TRY EXCEPT LOOP
                tableName = tableNames(k);
                if (tableNamesBool(k) == 0)
                    try
                        % GET OPTIONS DATA
                        ticker = tableName{1};
                        ticker = ticker(2:length(ticker));

                        d = getOptionsData(ticker,1);
                        exportArray = {today d{1}.ticker d{1}.underlying d{1}.s d{1}.optionType d{1}.strike d{1}.expiry...
                                       d{1}.price d{1}.bid d{1}.ask d{1}.volume d{1}.openInterest ...
                                       d{1}.bsVol d{1}.bsDelta d{1}.bsGamma d{1}.bsTheta d{1}.bsVega};

                        for i = 2:length(d)
                            current = {today d{i}.ticker d{i}.underlying d{i}.s d{i}.optionType d{i}.strike d{i}.expiry...
                                       d{i}.price d{i}.bid d{i}.ask d{i}.volume d{i}.openInterest ...
                                       d{i}.bsVol d{i}.bsDelta d{i}.bsGamma d{i}.bsTheta d{i}.bsVega};
                            exportArray = cat(1 , exportArray, current);
                        end

                        % EXPORT
                        fastinsert(conn, tableName{1}, colNames, exportArray) 
                        disp(['COMPLETED DOWNLOAD: ' ticker])
                        tableNamesBool(k) = 1;
                    catch ME
                        disp(['ERROR ON DOWNLOAD: ' ticker])
                        disp(ME.message);
                    end
                end
            end
        end

        % SEND NOTIFICATION EMAIL
        message = ['Successfully uploaded data for: ' 10 10 strjoin(tableNames, ', ') 10 10 'On: ' datestr(now)];
        matlabmail('popik@mit.edu', message, ['Option Upload Complete: ' datestr(today, 'mm/dd/yy')]);
    end

    exit()
end


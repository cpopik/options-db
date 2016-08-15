% MATLABMAIL Send an email from a predefined gmail account.

function matlabmail(recipient, message, subject)

    if nargin<4
        sender = 'cpopik13@gmail.com';
        psswd = 'popik2357';
    end

    setpref('Internet','E_mail',sender);
    setpref('Internet','SMTP_Server','smtp.gmail.com');
    setpref('Internet','SMTP_Username',sender);
    setpref('Internet','SMTP_Password',psswd);

    props = java.lang.System.getProperties;
    props.setProperty('mail.smtp.auth','true');
    props.setProperty('mail.smtp.socketFactory.class', ...
                      'javax.net.ssl.SSLSocketFactory');
    props.setProperty('mail.smtp.socketFactory.port','465');

    sendmail(recipient, subject, message);
end

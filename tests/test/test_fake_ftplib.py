import sys
import ftplib
import pytest
import fsx
import fsx.ftplib
from fsx.test import fsx_fake


@pytest.mark.parametrize('fsdict, query_path, exp', [
    ({
        'ftp://ftp.python.org': {
            'd1': {},
            'd2': {},
        },
    }, '/', ['d1', 'd2']),
    ({
        'ftp://ftp.python.org': {
            'd1': {
                'd2': {},
            },
        },
    }, '/d1', ['d2']),
    ({
        'ftp://ftp.python.org': {
            'd1': {
                'd2': {},
            },
        },
    }, 'd1', ['d2']),
])
def test_nlst_works(fsdict, query_path, exp, fsx_fake):
    fsx_fake.add_dict(fsdict)
    ftp = fsx.ftplib.FTP('ftp.python.org')
    ftp.login('user', 'passwd')
    ftp.prot_p()

    res = ftp.nlst(query_path)
    assert set(res) == set(exp)

@pytest.mark.parametrize('fsdict, file_path, exp', [
    ({
        'ftp://ftp.python.org': {
            'f1': 'somecontent',
        },
        'C:/tmp': {},
    }, 'f1', 'somecontent'),
    ({
        'ftp://ftp.python.org': {
            'f1': 'somecontent',
        },
        'C:/tmp': {},
    }, '/f1', 'somecontent'),
    ({
        'ftp://ftp.python.org': {
            'f1': 'foo\nbar',
        },
        'C:/tmp': {},
    }, 'f1', 'foo\nbar'),
])
def test_retrbinary_works(fsdict, file_path, exp, fsx_fake):
    fsx_fake.add_dict(fsdict)
    ftp = fsx.ftplib.FTP('ftp.python.org')
    ftp.login('user', 'passwd')
    ftp.prot_p()

    with fsx.open('C:/tmp/f1', 'wb') as file_:
        ftp.retrbinary('RETR '+file_path, file_.write)
    res = fsx.open('C:/tmp/f1').read()
    assert res == exp

@pytest.mark.parametrize('fp, server_path, content', [
    ('f1',  'ftp://ftp.python.org/f1', 'somecontent'),
    ('/f1', 'ftp://ftp.python.org/f1', 'somecontent'),
])
def test_storbinary_creates_file_on_server(fp, server_path, content, fsx_fake):
    fsx_fake.add_dict({'ftp://ftp.python.org': {}, 'src.txt': content})
    ftp = fsx.ftplib.FTP('ftp.python.org')
    ftp.login('user', 'passwd')
    ftp.prot_p()

    ftp.storbinary('STOR '+fp, fsx.open('src.txt', 'rb'))

    res = fsx.open(server_path, 'r').read()
    assert res == content

@pytest.mark.parametrize('pathname', [
    'd1',
    'd1/d2',
])
def test_mkd_creates_directories(pathname, fsx_fake):
    fsx_fake.add_dict({'ftp://ftp.python.org': {}})
    ftp = fsx.ftplib.FTP('ftp.python.org')
    ftp.login('user', 'passwd')
    ftp.prot_p()

    ftp.mkd(pathname)

    assert fsx.isdir('ftp://ftp.python.org/'+pathname)

# --- Errors ---
def test_nlst_raises_if_not_logged_in(fsx_fake):
    ftp = fsx.ftplib.FTP('ftp.python.org')
    with pytest.raises(ftplib.error_perm):
        ftp.nlst('/')

def test_prot_p_raises_if_not_logged_in(fsx_fake):
    ftp = fsx.ftplib.FTP('ftp.python.org')
    with pytest.raises(AttributeError):
        ftp.prot_p()

def test_retrbinary_raises_if_not_logged_in(fsx_fake):
    ftp = fsx.ftplib.FTP('ftp.python.org')
    with pytest.raises(ftplib.error_perm):
        ftp.retrbinary('RETR f1', sys.stdout)

def test_retrbinary_raises_if_file_doesnt_exist(fsx_fake):
    fsx_fake.add_dict({'ftp://ftp.python.org': {}})
    ftp = fsx.ftplib.FTP('ftp.python.org')
    ftp.login('user', 'passwd')
    ftp.prot_p()

    with pytest.raises(ftplib.error_perm):
        ftp.retrbinary('RETR f1', sys.stdout)

def test_storbinary():
    pass

from distutils.core import setup, Extension
from zipfile import ZipFile
from commands import getoutput

import os, sys

import generate_uno

def unopkg():
    generate_uno.main(os.path.join('unopkg', 'menu_def'),
                      os.path.join('unopkg', 'klaasculator_oo.py'),
                      os.path.join('unopkg', 'menu.xcu'))
    # try:
        # os.mkdir('gnumeric')
    # except:
        # pass
    # generate_uno.gnumeric(os.path.join('unopkg', 'menu_def'),
                          # os.path.join('gnumeric', 'klaasculator_gnumeric.py'),
                          # os.path.join('gnumeric', 'menu.xml'),
                          # os.path.join('gnumeric', 'plugin.xml'))
    
    try:
        os.mkdir('build')
    except:
        pass
    p = 'unopkg'
    z = ZipFile(os.path.join('build', 'klaasculator_3.uno.pkg'), 'w')
    z.write(os.path.join(p, 'klaasculator_oo.py'), 'klaasculator_oo.py')
    z.write(os.path.join(p, 'menu.xcu'), 'menu.xcu')
    z.write(os.path.join(p, 'klaasculator_3.xcu'), 'klaasculator_3.xcu')
    z.write(os.path.join(p, 'META-INF', 'manifest.xml'), 'META-INF/manifest.xml')
    z.close()

if not '--nounopkg' in sys.argv:
    unopkg()

wi = False
for i in range(len(sys.argv)):
    if sys.argv[i] == 'windows_installer':
        sys.argv[i] = 'build'
        sys.argv.append('--build-lib=build/lib')
        wi = True
        break

setup(name = 'klaasculator',
      version = '3',
      description = 'klaasculator, derre versie',
      package_dir = {'klaasculator':'klaasculator'},
      packages = ['klaasculator'],
      author = 'Klaas Jacob de Vries',
      author_email = 'klaasjacobdevries@gmail.com',
      license = 'gpl',
      long_description = 'klaasculator, derde versie',
      url = 'http://www.cleopatra-groningen.nl',
      )

import compileall, tarfile, platform

def getoounopkg():
    if platform.system().startswith('Win'):
        import _winreg
        k = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\OpenOffice.org\\UNO\\InstallPath')
        oopath = _winreg.QueryValueEx(k, '')[0]
        k.Close()
        return '"%s"' % os.path.join(oopath, 'unopkg.exe')
    else:
        e = getoutput('which soffice')
        p = os.readlink(e)
        d = os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(e), p)))
        return os.path.join(d, 'unopkg')

if 'install' in sys.argv:
    os.system('%s add -f -v %s' % (getoounopkg(), os.path.join('build', 'klaasculator_3.uno.pkg')))

def getnsis():
    if platform.system().startswith('Win'):
        import _winreg
        k = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\NSIS')
        path = _winreg.QueryValueEx(k, '')[0]
        k.Close()
        return '"%s"' % os.path.join(path, 'makensis.exe')
    else:
        return 'makensis'

if wi:
    tf = tarfile.TarFile(os.path.join('pygtk', 'pygtk-bin-windows.tar'), 'r')
    tf.extractall(os.path.join('build', 'pygtk'))
    tf.close()

    compileall.compile_dir(os.path.join('build', 'lib'))
    try:
        ns = getnsis()
    except Exception, e:
        print e
        print 
        print 'Kon geen NSIS vinden.'
        print 'Te vinden op http://nsis.sourceforge.net'
        sys.exit(1)
    
    try:
        os.mkdir('dist')
    except:
        pass

    os.system('%s windows_installer.nsi' % ns)

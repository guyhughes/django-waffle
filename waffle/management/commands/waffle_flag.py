from __future__ import print_function

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from waffle.models import Flag


class Command(BaseCommand): 
    option_list = BaseCommand.option_list + (
        make_option('-l', '--list',
            action='store_true',
            dest='list_flag',
            default=None,
            help="List existing samples."),
        make_option('--everyone',
            action='store_true',
            dest='everyone',
            help="Activate flag for all users."),
        make_option('--allow',
            action='store_const',
            const="allow",
            dest='everyone',
            help="Allow flag to be activated by other settings."),
        make_option('--no-one',
            action='store_false',
            dest='everyone',
            help="Deactivate flag globally."),
        make_option('--percent', '-p',
            action='store',
            type='int',
            dest='percent',
            help=('Roll out the flag for a certain percentage of users. '
                  'Takes a number between 0.0 and 100.0')),
        make_option('--superusers',
            action='store_true',
            dest='superusers',
            default=None,
            help='Turn on the flag for Django superusers.'),
        make_option('--staff',
            action='store_true',
            dest='staff',
            default=None,
            help='Turn on the flag for Django staff.'),
        make_option('--authenticated',
            action='store_true',
            dest='authenticated',
            default=None,
            help='Turn on the flag for logged in users.'),
        make_option('--rollout', '-r',
            action='store_true',
            dest='rollout',
            default=None,
            help='Turn on rollout mode.'),
        make_option('--create',
            action='store_true',
            dest='create',
            default=None,
            help='If the flag doesn\'t exist, create it.'),
    )

    help = "Modify a flag."
    args = "<flag_name>"

    def handle(self, flag_name=None, *args, **options):
        list_flag = options['list_flag']

        def __print_flag_field(field, value):
            print('{: >13s}: {:s}'.format(field, value))

        if list_flag:
            print('Flags:')

            for flag in Flag.objects.iterator():
                print('\n{:-<80s}'.format(flag.name))
                __print_flag_field('SUPERUSERS', flag.superusers)
                __print_flag_field('EVERYONE', flag.everyone)
                __print_flag_field('AUTHENTICATED', flag.authenticated)
                __print_flag_field('PERCENT', flag.percent)
                __print_flag_field('TESTING', flag.testing)
                __print_flag_field('ROLLOUT', flag.rollout)
                __print_flag_field('STAFF', flag.staff)

            return

        if not flag_name:
            raise CommandError("You need to specify a flag name.")

        if options['create']:
            flag, created = Flag.objects.get_or_create(name=flag_name)
            if created:
                print('Created flag: {:}'.format(flag_name))
        else:
            try:
                flag = Flag.objects.get(name=flag_name)
                print("Modifying flag: {:}".format(flag_name))
            except Flag.DoesNotExist:
                raise CommandError("This flag doesn't exist")

        # Loop through all options, setting Flag attributes that
        # match (ie. don't want to try setting flag.verbosity)
        for option in options:
            if hasattr(flag, option):
                __print_flag_field(option, options[option])
                setattr(flag, option, options[option])

        flag.save()

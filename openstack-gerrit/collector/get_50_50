#!/usr/bin/env perl

# gets even amounts of pass and fail

use List::Util 'shuffle';



open my $handle, '<', "changes.csv";
chomp(my @lines = <$handle>);
close $handle;

my @out;

my @pass;
my @fail;

my $first;
my $t = 0;
foreach (@lines) {
    if ($t == 0) {
        $first = $_;
        $t = 1;
    }
    else{
        if (substr($_, 0, 1) == "0") {
            push @fail, $_;
        }
        else
        {
            push @pass, $_;
        }
    }

}

@pass = shuffle(@pass);
@fail = shuffle(@fail);

my $p = scalar @pass;
my $f = scalar @fail;

if ( $p < $f){
    for (my $var = 0; $var < $p; $var++) {
        push @out, pop(@pass);
        push @out, pop(@fail);
    }
}
else{
    for (my $var = 0; $var < $f; $var++) {
        push @out, pop(@fail);
        push @out, pop(@pass);

    }
}

@out = shuffle(@out);

my $o = scalar @out;

print "$f, $p, $o\n";

open OUTPUT, ">", "changes_even.csv" or die "The Output didnt save";
print OUTPUT "$first\n";
foreach $i (@out)
{
	chomp $i;
	print OUTPUT "$i\n";
}
close OUTPUT;


from itertools import zip_longest
import re


class Version:
    def __init__(self, version):
        self.version = version

    def __eq__(self, other):
        version_self = Version.scrape_numbers(self.version)
        version_other = Version.scrape_numbers(other.version)
        result = Version.compare_version_lists(version_self, version_other)
        if result == 0:
            return True
        else:
            return False

    def __ne__(self, other):
        version_self = Version.scrape_numbers(self.version)
        version_other = Version.scrape_numbers(other.version)
        result = Version.compare_version_lists(version_self, version_other)
        if result != 0:
            return True
        else:
            return False

    def __lt__(self, other):
        version_self = Version.scrape_numbers(self.version)
        version_other = Version.scrape_numbers(other.version)
        result = Version.compare_version_lists(version_self, version_other)
        if result < 0:
            return True
        else:
            return False

    def __gt__(self, other):
        version_self = Version.scrape_numbers(self.version)
        version_other = Version.scrape_numbers(other.version)
        result = Version.compare_version_lists(version_self, version_other)
        if result > 0:
            return True
        else:
            return False

    def __le__(self, other):
        version_self = Version.scrape_numbers(self.version)
        version_other = Version.scrape_numbers(other.version)
        result = Version.compare_version_lists(version_self, version_other)
        if result <= 0:
            return True
        else:
            return False

    def __ge__(self, other):
        version_self = Version.scrape_numbers(self.version)
        version_other = Version.scrape_numbers(other.version)
        result = Version.compare_version_lists(version_self, version_other)
        if result >= 0:
            return True
        else:
            return False

    @staticmethod
    def scrape_numbers(version: str) -> list:
        """
        Scrape off the value of each rank of the version

        The string is split into ranks by points. Reduce each rank to the number and
        add it to the list. If 'ValueError' raise try to scrape off the number 
        at the beginning of the rank. If the number is missing assign '0'. 
        From the same rank scrape off the name of the version maturity. 
        Than substract the corresponding value: 'rc' - 0.25; 'b' - 0.5; 'a' - 0.75.
        Add the resulting number to the list.

        Parameters
        ----------
        version : str
            dot-separated values with maturity

        Raises
        ------
        ValueError
            failed to scrape version maturity

        Returns
        -------
        number_list : list
            list of numbers corresponding to each rank of the version
        """
        number_list = []
        for number in version.split("."):
            try:
                number_list.append(int(number))
            except ValueError:
                try:
                    raw_number = int(re.findall(r"\b\d+", number)[0])
                except IndexError:
                    raw_number = 0
                maturity = re.findall(r"[A-z]+", number)[0].lower()
                if maturity in ("rc", "release-candidate", "release_candidate"):
                    raw_number -= 0.25
                elif maturity in ("b", "beta"):
                    raw_number -= 0.5
                elif maturity in ("a", "alpha"):
                    raw_number -= 0.75
                else:
                    raise ValueError("failed to process value")
                number_list.append(raw_number)
        return number_list

    @staticmethod
    def compare_version_lists(version_self: list, version_other: list) -> int:
        """
        Compare the values of two lists sequentially

        Combine two lists using 'zip_longest' and compare the values.
        If the values are equal the next pair is compared. If the values are not
        equal, the diffrence between the first and second values is returned.
        If all pares are equal, return '0'.

        Parameters
        ----------
        version_self : str
            list of numbers of the first version
        version_other : str
            list of numbers of the secon version

        Returns
        -------
        value : int
            diffrence if the pair values are not equal and '0' otherwise
        """
        comparison_list = zip_longest(version_self, version_other, fillvalue=0)
        for value_1, value_2 in comparison_list:
            if value_1 == value_2:
                continue
            else:
                return value_1 - value_2
        else:
            return 0


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), "le failed"
        assert Version(version_2) > Version(version_1), "ge failed"
        assert Version(version_2) != Version(version_1), "neq failed"


if __name__ == "__main__":
    main()
